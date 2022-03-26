from django.urls import path
from recipes import views


urlpatterns = [
    path("", views.recipe_list, name="recipes"),
    path("create/", views.recipe_create_view, name="create_recipe"),
    path("<int:pk>/update/",
         views.RecipeEditView.as_view(),
         name="update_recipe"),
    path("<int:pk>/delete/",
         views.RecipeDeleteView.as_view(),
         name="delete_recipe"),
    path("<int:recipe_pk>/ingredients/add",
         views.add_ingredient,
         name="add_ingredient"),
    path("<int:recipe_pk>/ingredients/<int:pk>/edit/",
         views.RecipeIngredientEditView.as_view(),
         name="edit_recipe_ingredient"),
    path("<int:recipe_pk>/ingredients/<int:pk>/delete/",
         views.recipe_ingredient_delete_view,
         name="delete_recipe_ingredient"),
]
