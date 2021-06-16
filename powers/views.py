from django.shortcuts import render
from rest_framework import generics, permissions, status
from core.permissions import BaseOrderPermission
from .serializers import *
from utils.views import CustomGetCreateUpdateView


class GetCreateUpdatePersonalWelfareView(CustomGetCreateUpdateView):
    serializer_class = PersonalWelfareSerializer


class GetCreateUpdatePropertyAndAffairsView(CustomGetCreateUpdateView):
    serializer_class = PropertyAndAffairsSerializer
