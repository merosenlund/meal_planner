from django import forms
from meals.models import Meal


class MealOrderForm(forms.Form):
    meals = forms.ModelMultipleChoiceField(
        queryset=Meal.objects.filter(order=None),
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        labels = {
            "meals": "Meals not on any orders:"
        }
