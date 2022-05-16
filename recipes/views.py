from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic.edit import UpdateView, DeleteView
from django.db import IntegrityError

from recipes.models import (
  Recipe,
  RecipeIngredient,
)
from recipes.forms import (
    RecipeForm,
    RecipeIngredientForm,
)


# TODO - Change this into a Class View
@login_required
def recipe_list(request):
    recipes = Recipe.objects.all().order_by("-is_active")
    context = {
        "section": "recipes",
        "recipes": recipes,
    }
    return render(request, "recipes/list.html", context)


# TODO - Change this into a Class View
@login_required
def recipe_create_view(request):
    if request.method == "POST":
        form = RecipeForm(request.POST)
        if form.is_valid():
            recipe = form.save()
            messages.success(request, "Recipe created.")
            return redirect(reverse("update_recipe", args=[recipe.id]))
    else:
        form = RecipeForm()
        context = {"section": "recipes", "form": form}
        return render(request, "recipes/create.html", context)


class RecipeEditView(LoginRequiredMixin, UpdateView):
    model = Recipe
    fields = ["name", "is_active"]
    template_name = "recipes/update.html"
    success_url = reverse_lazy("recipes")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["section"] = "recipes"
        # Form for adding ingredients
        context["ingredient_form"] = RecipeIngredientForm()
        return context


class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipe
    success_url = reverse_lazy("recipes")
    template_name = "recipes/delete.html"


@login_required
def add_ingredient(request, recipe_pk):
    if request.method == "POST":
        form = RecipeIngredientForm(request.POST)
        if form.is_valid():
            ingredient = form.save(commit=False)
            recipe = Recipe.objects.get(pk=recipe_pk)
            ingredient.recipe = recipe
            try:
                ingredient.save()
            except IntegrityError:
                messages.add_message(request,
                                     messages.ERROR,
                                     "That ingredient has already been added.")
            else:
                messages.success(request, "Ingredient added.")
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 "Something went wrong.")
    return redirect(reverse("update_recipe", args=[recipe_pk]))


class RecipeIngredientEditView(LoginRequiredMixin, UpdateView):
    model = RecipeIngredient
    fields = ["ingredient", "serving"]
    template_name = "recipe_ingredients/update.html"
    success_url = reverse_lazy("recipes")

    def get_success_url(self):
        url = reverse("update_recipe", args=[self.object.recipe.id])
        return url


# TODO - Change this into a Class View (I'm not sure if I should change this. It definitely seems like it is overly simplified)
@login_required
def recipe_ingredient_delete_view(request, recipe_pk, pk):
    RecipeIngredient.objects.get(pk=pk).delete()
    return redirect(reverse("update_recipe", args=[recipe_pk]))
