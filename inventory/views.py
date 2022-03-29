from django.shortcuts import render
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from ingredients.models import Ingredient


class InventoryListView(LoginRequiredMixin, ListView):
    model = Ingredient
    template_name = "inventory/list.html"
    context_object_name = "inventory_items"

    def get_queryset(self):
        return Ingredient.objects.filter(needed__gt=20)
