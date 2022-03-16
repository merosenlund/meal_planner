from django import forms
from django.forms import ModelForm, Form

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


class MealOrderForm(Form):
    meals = forms.ModelMultipleChoiceField(
        queryset=Meal.objects.filter(order=None),
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        labels = {
            "meals": "Meals not on any orders:"
        }
