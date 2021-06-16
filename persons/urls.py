from django.urls import path

from . import views

app_name = "persons"

urlpatterns = [
    path(
        "listEntities/",
        views.ListEntitiesView.as_view(),
        name="list-entities",
    ),
    path(
        "order/<str:order_pk>/person/",
        views.RetrieveUpdateDestroyPersonalDetailsView.as_view(),
        name="list-create-people",
    ),
    path(
        "order/<str:order_pk>/person/<int:person_pk>/",
        views.RetrieveUpdateDestroyPersonalDetailsView.as_view(),
        name="update-people",
    ),
    path(
        "order/<str:order_pk>/charity/",
        views.RetrieveUpdateDestroyCharityView.as_view(),
        name="list-create-charity",
    ),
    path(
        "order/<str:order_pk>/charity/<int:charity_pk>/",
        views.RetrieveUpdateDestroyCharityView.as_view(),
        name="update-charity",
    ),
    path(
        "order/<str:order_pk>/appointments/",
        views.RetrieveUpdateDestroyAppointmentView.as_view(),
        name="update-appointment",
    ),
    path(
        "order/<str:order_pk>/donee_powers/",
        views.ListCreateDoneePowersView.as_view(),
        name="list-create-donee-powers",
    ),
    path(
        "order/<str:order_pk>/donee_powers/<int:donee_powers_pk>/",
        views.RetrieveUpdateDestroyDoneePowersView.as_view(),
        name="update-donee-powers",
    ),
]
