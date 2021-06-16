"""WillCraft URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import subprocess

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import TemplateView
from oauth2_provider.models import get_application_model
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class AdminConfigRetrieveView(APIView):

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        application = get_application_model().objects.get(name="WillCraft")
        data = {
            "facebook_tracking_id": getattr(settings, "FACEBOOK_TRACKING_ID", None),
            "tracking_debug": getattr(settings, "TRACKING_DEBUG", None),
            "ga_tracking_id": getattr(settings, "GA_TRACKING_ID", None),
            "stripe_key": getattr(settings, "STRIPE_PUBLISHABLE", None),
            "client_id": application.client_id,
        }
        return Response(data)


urlpatterns = [
    url(r"admin/", admin.site.urls),
    # Auth Apps
    path("auth/", include("willcraft_auth.urls")),
    # required for user details endpoint
    path("auth/", include("rest_auth.urls")),
    # Core functionality urls
    path("", include("lambda_service.urls")),
    path("", include("core.urls")),
    path("", include("persons.urls")),
    path("", include("assets.urls")),
    path("", include("lastrites.urls")),
    path("", include("powers.urls")),
    # Billing urls
    path("billing/", include("billing.urls")),
    # Partner urls
    path("partners/", include("partners.urls")),
    url(r'^docs/', include('docs.urls')),
    # Legal Services urls
    path("legal_service/", include("lawyer_services.urls")),
    # Misc - Views unrelated to main functionality
    path("content/", include("content.urls")),
    url("adminconfig/", AdminConfigRetrieveView.as_view()),
]

if getattr(settings, 'SILK', None):
    urlpatterns += [url(r"^silk/", include("silk.urls", namespace="silk"))]

urlpatterns = urlpatterns + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
)
urlpatterns = urlpatterns + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

urlpatterns.append(
    url(r"ˆ*", TemplateView.as_view(template_name="index.html")))
