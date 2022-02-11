from django.shortcuts import render

from .models import Recipe


# Create your views here.
def meal_list(request):
    return render(request, "meals/meal_list.html", {"section": "meals"})


def recipe_list(request):

    recipes = Recipe.objects.filter(is_active=True)

    context = {
        "section": "recipes",
        "recipes": recipes,
    }

    return render(request, "meals/recipe_list.html", context)
