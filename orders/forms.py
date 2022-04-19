from django import forms
from meals.models import Meal
from orders.models import Order


class MealOrderForm(forms.Form):
    meals = forms.ModelMultipleChoiceField(
        queryset=Meal.objects.filter(order=None),
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        labels = {
            "meals": "Meals not on any orders:",
        }


class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["date", "is_complete"]
        labels = {
            "is_complete": "Purchased"
        }
