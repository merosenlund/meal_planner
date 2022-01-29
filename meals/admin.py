from django.contrib import admin
from .models import Recipe, MealIngredient, Ingredient, Meal, PO


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(MealIngredient)
class MealIngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    pass


@admin.register(PO)
class POAdmin(admin.ModelAdmin):
    pass
