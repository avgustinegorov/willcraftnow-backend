from django.contrib import admin

from .models import *

# Register your models here.


class FirmAdminManager(admin.ModelAdmin):

    list_display = [
        "name",
        "email",
        "description",
        "has_gst_number",
        "tncs_file",
        "contact_number",
    ]


admin.site.register(Firm, FirmAdminManager)


class WitnessServiceAdminManager(admin.ModelAdmin):

    list_display = ["id", "order", "firm", "service_type", "review_type"]


admin.site.register(WitnessService, WitnessServiceAdminManager)


class ReviewServiceAdminManager(admin.ModelAdmin):

    list_display = ["id", "order", "firm", "service_type", "review_type"]


admin.site.register(ReviewService, ReviewServiceAdminManager)


class LPACertificateServiceAdminManager(admin.ModelAdmin):

    list_display = ["id", "order", "firm", "service_type", "review_type"]


admin.site.register(LPACertificateService, LPACertificateServiceAdminManager)
