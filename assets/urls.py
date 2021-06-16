from django.urls import path

from . import views

app_name = "assets"

urlpatterns = [
    path(
        "listAssets/",
        views.ListAssetView.as_view(),
        name="list-asset",
    ),
    path(
        "list_assets/",
        views.ListAssetView.as_view(),
        name="list-asset",
    ),
    path(
        "order/<str:order_pk>/assets/<str:asset_type>/",
        views.RetrieveUpdateDestroyAssetView.as_view(),
        name="create-asset",
    ),
    path(
        "order/<str:order_pk>/assets/<str:asset_type>/<int:asset_pk>/",
        views.RetrieveUpdateDestroyAssetView.as_view(),
        name="retrieve-update-destroy-asset",
    ),
    path(
        "order/<str:order_pk>/assets/<int:asset_pk>/allocations/",
        views.RetrieveUpdateDestroyAllocationView.as_view(),
        name="create-allocations",
    ),
    path(
        "order/<str:order_pk>/allocations/<int:allocation_pk>/",
        views.RetrieveUpdateDestroyAllocationView.as_view(),
        name="retrieve-update-destroy-allocation",
    ),
]
