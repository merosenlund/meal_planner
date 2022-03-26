from django.urls import path
from ingredients import views


urlpatterns = [
    path("recipes/<int:recipe_pk>/ingredients/create/",
         views.IngredientCreateView.as_view(),
         name="create_ingredient"),
]
