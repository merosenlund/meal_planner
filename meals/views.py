import io
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.views.generic.list import ListView
from django.urls import reverse, reverse_lazy
from django.http import FileResponse
from datetime import datetime
from django.db import IntegrityError

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from .models import Ingredient, Order, Recipe, Meal, RecipeIngredient
from .forms import MealForm, MealOrderForm, RecipeForm, RecipeIngredientForm


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
    fields = ["date", "recipe", "planned", "actual"]
    template_name = "meals/update.html"
    success_url = reverse_lazy("meals")


class MealDeleteView(LoginRequiredMixin, DeleteView):
    model = Meal
    success_url = reverse_lazy("meals")
    template_name = "meals/delete.html"


@login_required
def recipe_list(request):
    recipes = Recipe.objects.all().order_by("-is_active")
    context = {
        "section": "recipes",
        "recipes": recipes,
    }
    return render(request, "recipes/list.html", context)


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
    return render(request, "meals/create.html", context)


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
        return render(request, "recipes/create.html", context)


class RecipeEditView(LoginRequiredMixin, UpdateView):
    model = Recipe
    fields = ["name", "is_active"]
    template_name = "recipes/update.html"
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
    template_name = "recipes/delete.html"


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
    template_name = "recipe_ingredients/update.html"
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
    template_name = "ingredients/create.html"
    success_url = reverse_lazy("create_ingredient")

    def get_success_url(self):
        url = reverse("update_recipe", args=[self.kwargs.get("recipe_pk")])
        return url


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["section"] = "orders"
        return context


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    fields = ["date"]
    template_name = "orders/create.html"

    def get_success_url(self):
        return reverse("update_order", args=[self.object.id])


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    fields = ["date", "is_complete"]
    template_name = "orders/update.html"
    success_url = reverse_lazy("orders")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meal_form"] = MealOrderForm()
        context["section"] = "orders"
        meal_count = context["meal_form"].fields["meals"].queryset.count()
        context["no_meals"] = meal_count == 0
        return context


@login_required
def add_meals_to_order(request, pk):
    if request.method == "POST":
        form = MealOrderForm(request.POST)
        if form.is_valid():
            meals = form.cleaned_data["meals"]
            order = Order.objects.get(pk=pk)
            for meal in meals:
                meal.order = order
                meal.save()
    return redirect(reverse("update_order", args=[pk]))


@login_required
def remove_meal_from_order(request, pk, meal_pk):
    meal = Meal.objects.get(pk=meal_pk)
    order = Order.objects.get(pk=pk)
    order.meals.remove(meal)
    return redirect(reverse("update_order", args=[pk]))


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


@login_required
def print_orders(request):
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.platypus import Paragraph, Frame, Table, TableStyle

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle("Order List")
    p.setFont("Helvetica", 10)

    today = datetime.now().date()
    orders = Order.objects.filter(date__gte=today)

    styles = getSampleStyleSheet()
    title_style = styles["Title"]

    for order in orders:
        story = []

        story.append(Paragraph("Purchase Order", title_style))

        header_data = [
            ["Order #:", order.id]
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
            "Have",
            "Need",
        ]]

        ingredients = order.get_ingredients()

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
    return FileResponse(buffer, filename='orders.pdf')
