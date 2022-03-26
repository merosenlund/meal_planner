from django.urls import path
from . import views


urlpatterns = [
    path("", views.meal_list, name="meals"),
    path("<int:pk>/edit/", views.MealEditView.as_view(), name="edit_meal"),
    path("<int:pk>/delete/",
         views.MealDeleteView.as_view(),
         name="delete_meal"),
    path("<int:pk>/add_fruits_and_veggies/",
         views.add_fruits_and_veggies,
         name="add_fruits_and_veggies"),
    path("<int:meal_pk>/fruit/create/",
         views.FruitCreateView.as_view(),
         name="create_fruit"),
    path("<int:meal_pk>/vegetable/create/",
         views.VeggieCreateView.as_view(),
         name="create_vegetable"),
    path("schedule/", views.meal_create_view, name="schedule_meal"),
    path("print/", views.print_meals, name="print_meal"),
]
