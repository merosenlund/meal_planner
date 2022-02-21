from django.urls import path
from . import views


urlpatterns = [
    path("", views.meal_list, name="meals"),
    path("recipes/", views.recipe_list, name="recipes"),
    path("schedule/", views.meal_form_view, name="schedule_meal"),
    path("recipes/create/", views.recipe_create_view, name="create_recipe"),
]
