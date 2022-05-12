import io
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse, reverse_lazy
from django.http import FileResponse
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from meals.models import Meal
from meals.forms import (
    MealForm,
    FruitAndVeggieForm,
)
from ingredients.models import (
    Ingredient,
)


@login_required
def meal_list(request):
    today = datetime.now().date()
    meals = Meal.objects.filter(date__gte=today)
    context = {
        "section": "meals",
        "meals": meals,
    }
    return render(request, "meals/list.html", context)


class MealEditView(LoginRequiredMixin, UpdateView):
    model = Meal
    fields = ["date",
              "recipe",
              "planned",
              "actual",
              "fruit",
              "fruit_serving",
              "vegetable",
              "vegetable_serving"]
    template_name = "meals/update.html"
    success_url = reverse_lazy("meals")


class MealDeleteView(LoginRequiredMixin, DeleteView):
    model = Meal
    success_url = reverse_lazy("meals")
    template_name = "meals/delete.html"


@login_required
def meal_create_view(request):
    if request.method == "POST":
        meal_form = MealForm(request.POST)
        if meal_form.is_valid():
            meal = meal_form.save()
            fruit = Ingredient.objects.get(name="fruit")
            veggie = Ingredient.objects.get(name="vegetable")
            ingredients = meal.recipe.ingredients.all()
            messages.add_message(request, messages.SUCCESS, "Meal scheduled.")
            if fruit in ingredients or veggie in ingredients:
                return redirect(reverse("add_fruits_and_veggies",
                                        args=[meal.id]))
            else:
                return redirect(reverse("meals"))
    else:

        last_meal = Meal.objects.all().order_by("id").last()
        if last_meal:
            default_planned = last_meal.planned
        else:
            default_planned = 0
        meal_form = MealForm(initial={"planned": default_planned})
    context = {
        "section": "meals",
        "form": meal_form,
    }
    return render(request, "meals/create.html", context)


@login_required
def add_fruits_and_veggies(request, pk):
    meal = Meal.objects.get(pk=pk)
    ingredients = meal.recipe.ingredients.all()
    fruit = Ingredient.objects.get(name="fruit")
    veggie = Ingredient.objects.get(name="vegetable")
    has_veggies = veggie in ingredients
    has_fruit = fruit in ingredients
    context = {
        "meal": meal,
        "has_veggies": has_veggies,
        "has_fruit": has_fruit
    }

    if request.method == "GET":
        context["form"] = FruitAndVeggieForm()
    else:
        form = FruitAndVeggieForm(request.POST)
        if form.is_valid():
            if has_fruit:
                meal.fruit = form.cleaned_data["fruit"]
                meal.fruit_serving = form.cleaned_data["fruit_quantity"]
            if has_veggies:
                meal.vegetable = form.cleaned_data["vegetable"]
                meal.vegetable_serving = (
                    form.cleaned_data["vegetable_quantity"]
                )
            meal.save()
            return redirect("meals")
        else:
            context["form"] = form

    return render(request, "meals/add.html", context)


class FruitCreateView(LoginRequiredMixin, CreateView):
    model = Ingredient
    fields = ["name", "uom"]
    template_name = "ingredients/fruit.html"

    def get_success_url(self):
        url = reverse("add_fruits_and_veggies",
                      args=[self.kwargs.get("meal_pk")])
        return url

    def form_valid(self, form):
        fruit = form.save(commit=False)
        fruit.type = "fruit"
        fruit.save()
        return redirect(self.get_success_url())


class VeggieCreateView(LoginRequiredMixin, CreateView):
    model = Ingredient
    fields = ["name", "uom"]
    template_name = "ingredients/veggie.html"

    def get_success_url(self):
        url = reverse("add_fruits_and_veggies",
                      args=[self.kwargs.get("meal_pk")])
        return url

    def form_valid(self, form):
        veggie = form.save(commit=False)
        veggie.type = "vegetable"
        veggie.save()
        return redirect(self.get_success_url())


@login_required
def print_meals(request):
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.platypus import Paragraph, Frame, Table, TableStyle

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle("Meal List")
    p.setFont("Helvetica", 10)

    today = datetime.now().date()
    meals = Meal.objects.filter(date__gte=today)

    styles = getSampleStyleSheet()
    title_style = styles["Title"]

    for meal in meals:
        story = []

        story.append(Paragraph("Record Sheet", title_style))

        name = meal.recipe.name.title()

        header_data = [
            ["Meal:", name],
            ["Date:", meal.date],
            ["# of pans of main dish:", ""],
            ["# of pans left:", ""]
        ]
        header_table = Table(
            header_data,
            colWidths=("*", 1.5*inch),
            spaceAfter=0.5*inch,
            spaceBefore=0.5*inch
        )

        header_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("LINEBELOW", (1, 0), (1, -1), 0.25, colors.black),
        ]))

        story.append(header_table)

        ingredient_data = [[
            "Ingredients",
            "Amount",
            "Put Out",
            "Left Over",
        ]]

        ingredients = meal.get_ingredients()

        for ingredient, [amount, uom] in ingredients.items():
            ingredient_data.append([
                ingredient.title(),
                f"{amount} {uom}",
            ])

        ingredient_table = Table(
            ingredient_data, colWidths=(4*inch, "*", "*", "*")
        )
        ingredient_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("LINEBELOW", (0, 0), (-1, 0), 2, colors.black),
            ("LINEBELOW", (0, 0), (-1, 0), 2, colors.black),
            ("ALIGN", (1, 0), (-1, 0), "CENTER")
        ]))

        story.append(ingredient_table)
        f = Frame(0.5*inch, 0.5*inch, 7.5*inch, 10*inch)
        f.hAlign = "LEFT"
        f.addFromList(story, p)
        p.showPage()

    p.save()

    buffer.seek(0)
    return FileResponse(buffer, filename='meals.pdf')
