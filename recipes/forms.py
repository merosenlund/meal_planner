from django.forms import ModelForm

from recipes.models import Recipe, RecipeIngredient


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ["name"]


class RecipeIngredientForm(ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["ingredient", "serving"]
        labels = {
            "ingredient": "Ingredient to Add",
            "serving": "Amount per person"
        }
