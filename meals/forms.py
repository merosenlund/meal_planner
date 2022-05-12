from django import forms
from django.forms import ModelForm, Form
from django.core.validators import MinValueValidator

from meals.models import Meal
from ingredients.models import Ingredient


class MealForm(ModelForm):
    class Meta:
        model = Meal
        fields = ["date", "recipe", "planned"]


class FruitAndVeggieForm(Form):
    vegetable = forms.ModelChoiceField(
        queryset=Ingredient.objects.filter(type="vegetable"),
        required=False
    )
    vegetable_quantity = forms.FloatField(
        required=False,
        label="Amount per person",
        validators=[MinValueValidator(0, message="Must be zero or greater")]
    )
    fruit = forms.ModelChoiceField(
        queryset=Ingredient.objects.filter(type="fruit"),
        required=False
    )
    fruit_quantity = forms.FloatField(
        required=False,
        label="Amount per person",
        validators=[MinValueValidator(0, message="Must be zero or greater")]
    )


class FruitForm(ModelForm):
    class Meta:
        model = Ingredient
        fields = ["name", "uom"]
        labels = {
            "uom": "Unit of Measure:"
        }
