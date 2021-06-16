from django.urls import path
from . import views

app_name = "lambda_service"

urlpatterns = [
    path(
        "order/<str:order_pk>/generate_pdf/",
        views.TestView.as_view(),
        name="generate-order-pdf",
    ),
]
