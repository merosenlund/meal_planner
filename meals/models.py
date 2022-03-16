from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=150, unique=True)
    uom = models.CharField(max_length=10)

    def __str__(self):
        return self.name.title()


class Recipe(models.Model):
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        through="RecipeIngredient"
    )

    def __str__(self):
        return self.name.title()


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    serving = models.FloatField()

    def __str__(self):
        return f"{self.ingredient} for {self.recipe}"

    class Meta:
        unique_together = ["recipe", "ingredient"]
        ordering = ["id"]


class PO(models.Model):
    date = models.DateField()
    is_complete = models.BooleanField(default=False)

    def get_ingredients(self):
        po_ingredients = {}

        for meal in self.meals:
            meal_ingredients = meal.get_ingredients()
            for ingredient, [amount, uom] in meal_ingredients.items():
                if po_ingredients.get(ingredient):
                    po_ingredients[ingredient][0] += amount
                else:
                    po_ingredients[ingredient] = [amount, uom]

        return po_ingredients


class Meal(models.Model):
    date = models.DateField()
    recipe = models.ForeignKey(
        Recipe,
        related_name="meal",
        on_delete=models.CASCADE
    )
    planned = models.SmallIntegerField(null=True, blank=True)
    actual = models.SmallIntegerField(null=True, blank=True)
    po = models.ForeignKey(
        PO,
        null=True, blank=True,
        related_name="meals",
        on_delete=models.PROTECT
    )

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
            if ingredients.get(ingredient):
                ingredients[ingredient][0] += amount
            else:
                ingredients[ingredient] = [amount, uom]
        return ingredients
