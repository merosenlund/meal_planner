import io
from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse
from django.http import FileResponse
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from .models import Recipe, Meal
from .forms import MealForm, RecipeForm


def meal_list(request):
    today = datetime.now().date()
    meals = Meal.objects.filter(date__gte=today)
    context = {
        "section": "meals",
        "meals": meals,
    }
    return render(request, "meals/meal_list.html", context)


def recipe_list(request):
    recipes = Recipe.objects.filter(is_active=True)
    context = {
        "section": "recipes",
        "recipes": recipes,
    }
    return render(request, "meals/recipe_list.html", context)


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


def print_meals(request):
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.platypus import Paragraph, Frame, Table, TableStyle

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle("Meal List")

    meals = Meal.objects.all()


    styles = getSampleStyleSheet()
    styleH = styles['Heading1']

    for meal in meals:
        data = [[
            "Ingredient",
            "Amount",
            "Put Out",
            "Left Over",
        ]]
        story = []
        name = meal.recipe.name
        story.append(Paragraph(name, styleH))
        for ingredient in meal.recipe.ingredients.all():
            data.append([
                ingredient.name,
                ingredient.uom,
            ])

        t = Table(data)
        t.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black)
        ]))

        story.append(t)
        f = Frame(0.5*inch, 0.5*inch, 7*inch, 10*inch, showBoundary=1)
        f.addFromList(story, p)

        # Close the PDF object cleanly, and we're done.
        p.showPage()

    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, filename='hello.pdf')
