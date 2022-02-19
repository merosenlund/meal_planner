from django.shortcuts import render
from datetime import datetime

from .models import Recipe, Meal
from .forms import MealForm


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
    else:
        meal_form = MealForm()
    context = {
        "section": "meals",
        "meal_form": meal_form,
    }
    return render(request, "meals/create_meal.html", context)
