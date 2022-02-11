from django.db import models


class Recipe(models.Model):
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name.title()


class Ingredient(models.Model):
    name = models.CharField(max_length=150, unique=True)
    uom = models.CharField(max_length=10)
    recipes = models.ManyToManyField(Recipe, related_name="ingredients", through="MealIngredient")

    def __str__(self):
        return self.name.title()


class MealIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    serving = models.DecimalField(max_digits=6, decimal_places=4)

    def __str__(self):
        return f"{self.ingredient} for {self.recipe}"

    class Meta:
        unique_together = ["recipe", "ingredient"]


class Meal(models.Model):
    date = models.DateField()
    recipe = models.ForeignKey(Recipe, related_name="meal", on_delete=models.CASCADE)
    planned = models.SmallIntegerField()
    actual = models.SmallIntegerField()

    def __str__(self):
        return self.name.title()


class PO(models.Model):
    date = models.DateField()
    meal = models.OneToOneField(Meal, related_name="po", on_delete=models.CASCADE)
