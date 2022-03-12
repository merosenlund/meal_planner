import io
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import FileResponse
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from .models import Recipe, Meal
from .forms import MealForm, RecipeForm


@login_required
def meal_list(request):
    today = datetime.now().date()
    meals = Meal.objects.filter(date__gte=today)
    context = {
        "section": "meals",
        "meals": meals,
    }
    return render(request, "meals/meal_list.html", context)


@login_required
def recipe_list(request):
    recipes = Recipe.objects.filter(is_active=True)
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
            form.save()
            messages.success(request, "Recipe created.")
            return redirect(reverse("recipes"))
    else:
        form = RecipeForm()
        context = {"section": "recipes", "form": form}
        return render(request, "meals/create_recipe.html", context)


@login_required
def print_meals(request):
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.platypus import Paragraph, Frame, Table, TableStyle

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle("Meal List")
    p.setFont("Helvetica", 10)

    meals = Meal.objects.all()

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

        for recipe_ingredient in meal.recipe.mealingredient_set.all():
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
