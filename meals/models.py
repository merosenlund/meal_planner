from django.db import models


class LowerCaseCharField(models.CharField):
    def get_prep_value(self, value):
        return str(value).lower()


class Ingredient(models.Model):
    name = LowerCaseCharField(max_length=150, unique=True)
    uom = models.CharField(max_length=10)
    type = models.CharField(default="standard",
                            max_length=50)

    def __str__(self):
        return self.name.title()

    class Meta:
        ordering = ["name"]


class Recipe(models.Model):
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        through="RecipeIngredient",
        limit_choices_to={"type": "standard"}
    )

    def __str__(self):
        return self.name.title()


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   limit_choices_to={"type": "standard"})
    serving = models.FloatField()

    def __str__(self):
        return f"{self.ingredient} for {self.recipe}"

    class Meta:
        unique_together = ["recipe", "ingredient"]
        ordering = ["id"]


class MealIngredient(models.Model):
    meal = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    Ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    total = models.PositiveSmallIntegerField()
    put_out = models.PositiveSmallIntegerField()
    left_over = models.PositiveSmallIntegerField()


class Order(models.Model):
    date = models.DateField()
    is_complete = models.BooleanField(default=False)

    class Meta:
        ordering = ["id", "-is_complete"]

    def get_ingredients(self):
        order_ingredients = {}

        for meal in self.meals.all():
            meal_ingredients = meal.get_ingredients()
            for ingredient, [amount, uom] in meal_ingredients.items():
                if order_ingredients.get(ingredient):
                    order_ingredients[ingredient][0] += amount
                else:
                    order_ingredients[ingredient] = [amount, uom]

        return order_ingredients

    def get_meal_count(self):
        return self.meals.count()


class Meal(models.Model):
    date = models.DateField()
    recipe = models.ForeignKey(
        Recipe,
        related_name="meal",
        on_delete=models.CASCADE
    )
    planned = models.SmallIntegerField(null=True, blank=True)
    actual = models.SmallIntegerField(null=True, blank=True)
    order = models.ForeignKey(
        Order,
        null=True, blank=True,
        related_name="meals",
        on_delete=models.PROTECT
    )
    fruit = models.ForeignKey(Ingredient,
                              on_delete=models.PROTECT,
                              null=True, blank=True,
                              related_name="meal_fruit",
                              limit_choices_to={"type": "fruit"})
    fruit_serving = models.FloatField(null=True, blank=True, default=0)
    vegetable = models.ForeignKey(Ingredient,
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
