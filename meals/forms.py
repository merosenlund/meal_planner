from dataclasses import fields
from django.forms import ModelForm

from .models import Meal


class MealForm(ModelForm):
    class Meta:
        model = Meal
        fields = ["date", "recipe", "planned"]