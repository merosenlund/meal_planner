from django import forms
from django.forms import ModelForm

from .models import Meal, Recipe, Ingredient


class MealForm(ModelForm):
    class Meta:
        model = Meal
        fields = ["date", "recipe", "planned"]


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ["name"]
