from django.urls import path
from ingredients import views


urlpatterns = [
    path("<int:recipe_pk>/create/",
         views.IngredientCreateView.as_view(),
         name="create_ingredient"),
]
