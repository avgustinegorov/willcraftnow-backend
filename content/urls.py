from django.urls import path

from .views import *

app_name = "content"

urlpatterns = [
    path("faq/", FAQListView.as_view(), name="faq-list"),
    path("tips_keywords/", TipsKeyWordsListView.as_view(), name="tips-keywords-list"),
]
