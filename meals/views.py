import io
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse, reverse_lazy
from django.http import FileResponse
from datetime import datetime
from django.db import IntegrityError

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from .models import Ingredient, Recipe, Meal, RecipeIngredient
from .forms import MealForm, RecipeForm, RecipeIngredientForm


@login_required
def meal_list(request):
    today = datetime.now().date()
    meals = Meal.objects.filter(date__gte=today)
    context = {
        "section": "meals",
        "meals": meals,
    }
    return render(request, "meals/meal_list.html", context)


class MealEditView(LoginRequiredMixin, UpdateView):
    model = Meal
    fields = ["date", "recipe", "planned", "actual"]
    template_name = "meals/update_meal.html"
    success_url = reverse_lazy("meals")


class MealDeleteView(LoginRequiredMixin, DeleteView):
    model = Meal
    success_url = reverse_lazy("meals")
    template_name = "meals/delete_meal.html"


@login_required
def recipe_list(request):
    recipes = Recipe.objects.all().order_by("-is_active")
    context = {
        "section": "recipes",
        "recipes": recipes,
    }
    return render(request, "meals/recipe_list.html", context)


@login_required
def meal_create_view(request):
    if request.method == "POST":
        meal_form = MealForm(request.POST)
        if meal_form.is_valid():
            meal_form.save()
            messages.add_message(request, messages.SUCCESS, "Meal scheduled.")
            return redirect(reverse("meals"))
    else:
        meal_form = MealForm()
    context = {
        "section": "meals",
        "form": meal_form,
    }
    return render(request, "meals/create_meal.html", context)


@login_required
def recipe_create_view(request):
    if request.method == "POST":
        form = RecipeForm(request.POST)
        if form.is_valid():
            recipe = form.save()
            messages.success(request, "Recipe created.")
            return redirect(reverse("update_recipe", args=[recipe.id]))
    else:
        form = RecipeForm()
        context = {"section": "recipes", "form": form}
        return render(request, "meals/create_recipe.html", context)


class RecipeEditView(LoginRequiredMixin, UpdateView):
    model = Recipe
    fields = ["name", "is_active"]
    template_name = "meals/update_recipe.html"
    success_url = reverse_lazy("recipes")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["section"] = "recipes"
        # Form for adding ingredients
        context["ingredient_form"] = RecipeIngredientForm()
        return context


class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipe
    success_url = reverse_lazy("recipes")
    template_name = "meals/delete_recipe.html"


@login_required
def add_ingredient(request, recipe_pk):
    if request.method == "POST":
        form = RecipeIngredientForm(request.POST)
        if form.is_valid():
            ingredient = form.save(commit=False)
            recipe = Recipe.objects.get(pk=recipe_pk)
            ingredient.recipe = recipe
            try:
                ingredient.save()
            except IntegrityError:
                messages.add_message(request,
                                     messages.ERROR,
                                     "That ingredient has already been added.")
            else:
                messages.success(request, "Ingredient added.")
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 "Something went wrong.")
    return redirect(reverse("update_recipe", args=[recipe_pk]))


class RecipeIngredientEditView(LoginRequiredMixin, UpdateView):
    model = RecipeIngredient
    fields = ["ingredient", "serving"]
    template_name = "meals/update_recipe_ingredient.html"
    success_url = reverse_lazy("recipes")

    def get_success_url(self):
        url = reverse("update_recipe", args=[self.object.recipe.id])
        return url


@login_required
def recipe_ingredient_delete_view(request, recipe_pk, pk):
    RecipeIngredient.objects.get(pk=pk).delete()
    return redirect(reverse("update_recipe", args=[recipe_pk]))


class IngredientCreateView(LoginRequiredMixin, CreateView):
    model = Ingredient
    fields = ["name", "uom"]
    template_name = "meals/create_ingredient.html"
    success_url = reverse_lazy("create_ingredient")

    def get_success_url(self):
        url = reverse("update_recipe", args=[self.kwargs.get("recipe_pk")])
        return url


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

        for recipe_ingredient in meal.recipe.recipeingredient_set.all():
            if meal.planned:
                amount = f"{meal.planned * recipe_ingredient.serving}"
                amount = amount.rstrip("0").rstrip(".")
            else:
                amount = 0

            uom = recipe_ingredient.ingredient.uom
            ingredient_data.append([
                recipe_ingredient.ingredient.name.title(),
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
