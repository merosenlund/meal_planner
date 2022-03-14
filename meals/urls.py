from django.urls import path
from . import views


urlpatterns = [
    path("", views.meal_list, name="meals"),
    path("<int:pk>/edit", views.MealEditView.as_view(), name="edit_meal"),
    path("<int:pk>/delete",
         views.MealDeleteView.as_view(),
         name="delete_meal"),
    path("recipes/", views.recipe_list, name="recipes"),
    path("schedule/", views.meal_create_view, name="schedule_meal"),
    path("recipes/create/", views.recipe_create_view, name="create_recipe"),
    path("recipes/<int:pk>/update/",
         views.RecipeEditView.as_view(),
         name="update_recipe"),
    path("print/", views.print_meals, name="print_meal"),
]
