from django.db import models


class Recipe(models.Model):
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=150)
    recipes = models.ManyToManyField(Recipe, through="MealIngredient")


class MealIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    serving = models.DecimalField(max_digits=6, decimal_places=4)


class Meal(models.Model):
    date = models.DateField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    planned = models.SmallIntegerField()
    actual = models.SmallIntegerField()


class PO(models.Model):
    date = models.DateField()
    meal = models.OneToOneField(Meal, on_delete=models.CASCADE)
