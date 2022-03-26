from django.db import models


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
