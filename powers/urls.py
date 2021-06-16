from django.urls import path
from .views import *

app_name = "powers"

urlpatterns = [
    path(
        "order/<order_pk>/personal_welfare/",
        GetCreateUpdatePersonalWelfareView.as_view(),
        name="create-retrieve-update-destroy-property-affairs",
    ),
    path(
        "order/<str:order_pk>/property_affairs/",
        GetCreateUpdatePropertyAndAffairsView.as_view(),
        name="create-retrieve-update-property-affairs",
    ),
]
