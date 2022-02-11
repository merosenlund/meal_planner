from django.urls import path
from . import views


urlpatterns = [
    path("", views.meal_list, name="meals"),
    path("recipes/", views.recipe_list, name="recipes"),
]
