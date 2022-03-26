from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView

from ingredients.models import (
  Ingredient,
)


class IngredientCreateView(LoginRequiredMixin, CreateView):
    model = Ingredient
    fields = ["name", "uom"]
    template_name = "ingredients/create.html"
    success_url = reverse_lazy("create_ingredient")

    def get_success_url(self):
        url = reverse("update_recipe", args=[self.kwargs.get("recipe_pk")])
        return url
