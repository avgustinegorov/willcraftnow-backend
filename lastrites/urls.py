from django.urls import path
from . import views

app_name = "lastrites"

urlpatterns = [
    path(
        "order/<str:order_pk>/lastrites/",
        views.GetCreateUpdateLastRitesView.as_view(),
        name="arrangements-lastrites",
    ),
    path(
        "order/<str:order_pk>/instructions/",
        views.GetCreateUpdateInstructionsView.as_view(),
        name="arrangements-instructions",
    ),
]
