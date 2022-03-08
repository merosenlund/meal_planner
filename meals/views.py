import io
from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse
from django.http import FileResponse
from reportlab.pdfgen import canvas
from datetime import datetime

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


def meal_form_view(request):
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
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, filename='hello.pdf')
