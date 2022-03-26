from django.contrib import admin
from meals.models import Meal


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    pass
