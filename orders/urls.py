from django.urls import path
from orders import views


urlpatterns = [
    path("orders/",
         views.OrderListView.as_view(),
         name="orders"),
    path("orders/create",
         views.OrderCreateView.as_view(),
         name="create_order"),
    path("orders/<int:pk>/update",
         views.OrderUpdateView.as_view(),
         name="update_order"),
    path("orders/<int:pk>/add_meals",
         views.add_meals_to_order,
         name="add_meals_to_order"),
    path("orders/<int:pk>/remove/<int:meal_pk>/",
         views.remove_meal_from_order,
         name="remove_meal_from_order"),
    path("orders/print/",
         views.print_orders,
         name="print_orders"),
]
