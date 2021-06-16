from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path(
        "order/create/<str:order_type>/",
        views.CreateOrderView.as_view(),
        name="create-order",
    ),
    path("order/list/", views.ListOrderView.as_view(), name="retrieve-list-order"),
    path(
        "order/<str:order_pk>/",
        views.RetrieveOrderView.as_view(),
        name="retrieve-order",
    ),
]
