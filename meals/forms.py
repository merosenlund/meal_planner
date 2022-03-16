from django.forms import ModelForm

from .models import Meal, Recipe, RecipeIngredient


class MealForm(ModelForm):
    class Meta:
        model = Meal
        fields = ["date", "recipe", "planned"]


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ["name"]


class RecipeIngredientForm(ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["ingredient", "serving"]
        labels = {
            "ingredient": "Ingredient to Add"
        }
