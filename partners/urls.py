from django.urls import path

from . import views

app_name = "partners"

urlpatterns = [
    path("", views.PartnersListView.as_view(), name="all_partners"),
    path("get_discount/", views.GetPartnerDiscount.as_view(), name="get_discount"),
]
