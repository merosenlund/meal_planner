from django.db import models
from django.core.validators import MinValueValidator


class Meal(models.Model):
    date = models.DateField()
    recipe = models.ForeignKey(
        "recipes.Recipe",
        related_name="meal",
        on_delete=models.CASCADE
    )
    planned = models.SmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0, message="Must be zero or larger")]
    )
    actual = models.SmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0, message="Must be zero or larger")]
    )
    order = models.ForeignKey(
        "orders.Order",
        null=True, blank=True,
        related_name="meals",
        on_delete=models.PROTECT
    )
    fruit = models.ForeignKey("ingredients.Ingredient",
                              on_delete=models.PROTECT,
                              null=True, blank=True,
                              related_name="meal_fruit",
                              limit_choices_to={"type": "fruit"})
    fruit_serving = models.FloatField(
        null=True,
        blank=True,
        default=0,
        validators=[MinValueValidator(0, message="Less than zero not allowed")]
    )
    vegetable = models.ForeignKey("ingredients.Ingredient",
                                  on_delete=models.PROTECT,
                                  null=True, blank=True,
                                  related_name="meal_vegatable",
                                  limit_choices_to={"type": "vegetable"})
    vegetable_serving = models.FloatField(null=True, blank=True, default=0)

    class Meta:
        ordering = ["date", "-actual"]

    def __str__(self):
        return f"{self.recipe.name} on {self.date}"

    def get_ingredients(self):
        ingredients = {}
        recipe_ingredients = self.recipe.recipeingredient_set
        if self.planned:
            planned = self.planned
        else:
            planned = 0

        for recipe_ingredient in recipe_ingredients.all():
            ingredient = recipe_ingredient.ingredient.name
            amount = round(recipe_ingredient.serving * planned)
            uom = recipe_ingredient.ingredient.uom
            if ingredient == "vegetable" and self.vegetable:
                ingredient = self.vegetable.name
                amount = round(self.vegetable_serving * planned)
                uom = self.vegetable.uom
            elif ingredient == "fruit" and self.fruit:
                ingredient = self.fruit.name
                amount = round(self.fruit_serving * planned)
                uom = self.fruit.uom
            if ingredients.get(ingredient):
                ingredients[ingredient][0] += amount
            else:
                ingredients[ingredient] = [amount, uom]
        return ingredients


class MealIngredient(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    Ingredient = models.ForeignKey("ingredients.Ingredient",
                                   on_delete=models.CASCADE)
    total = models.PositiveSmallIntegerField()
    put_out = models.PositiveSmallIntegerField()
    left_over = models.PositiveSmallIntegerField()
