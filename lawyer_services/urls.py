from django.urls import path
from . import views

app_name = "lawyer_services"

urlpatterns = [
    path(
        "order/<str:order_pk>/service/<str:service_type>/",
        views.RetrieveUpdateDestroyLegalServicesView.as_view(),
        name="retrieve-update-destroy-witness",
    ),
    path(
        "allFirms/",
        views.ListFirmView.as_view(),
        name="list-firms",
    ),
]
