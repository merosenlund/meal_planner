from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse
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
        context = {
            "section": "recipes",
            "form": form
        }
        return render(request, "meals/create_recipe.html", context)
