from django.conf.urls import url
from rest_framework.authentication import SessionAuthentication
from rest_framework.documentation import include_docs_urls
from rest_framework.permissions import IsAdminUser


api_title = 'WillCraft API'
description = """
This api just available by checking session permissions

"""

urlpatterns = [
    url(
        r'^', include_docs_urls(
            title=api_title, description=description,
            authentication_classes=(
                SessionAuthentication,
            ),
            permission_classes=(
                IsAdminUser,
            )
        )
    ),
]
