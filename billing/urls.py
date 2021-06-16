from django.urls import path
from . import views

app_name = "billing"

urlpatterns = [
    # TODO: frontend JS code doesn't trigger this URL. Remove it when it is really not used anywhere.
    path(
        "<str:order_pk>/latest_invoice/",
        views.RetrieveUpdateInvoiceView.as_view(),
        name="retrieve-update-latest-invoice",
    ),
    path(
        "<str:order_pk>/charge_stripe/",
        views.StripeOneOffChargeView.as_view(),
        name="stripe-one-off-charge",
    ),
    path(
        "<str:order_pk>/discount/",
        views.CreateDiscountView.as_view(),
        name="create-discount",
    ),
]
