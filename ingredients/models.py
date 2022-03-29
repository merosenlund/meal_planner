from django.db import models
from meal_planner.models import LowerCaseCharField


class Ingredient(models.Model):
    name = LowerCaseCharField(max_length=150, unique=True)
    uom = models.CharField(max_length=10)
    type = models.CharField(default="standard",
                            max_length=50)
    on_hand = models.PositiveSmallIntegerField()

    @property
    def needed(self):
        return 22

    def __str__(self):
        return self.name.title()

    class Meta:
        ordering = ["name"]
