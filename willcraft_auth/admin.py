# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from import_export import resources
from import_export.admin import ImportExportMixin

from .forms import WillCraftUserChangeForm, WillCraftUserCreationForm
from .models import *


class WillCraftUserAdminResource(resources.ModelResource):
    class Meta:
        model = WillCraftUser


class WillCraftUserAdmin(ImportExportMixin, UserAdmin):
    """Define admin model for custom User model with no email field."""

    add_form = WillCraftUserCreationForm
    form = WillCraftUserChangeForm
    model = WillCraftUser
    resource_class = WillCraftUserAdminResource

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {"classes": ("wide",), "fields": ("email", "password1", "password2"),},
        ),
    )
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "last_login",
        "referral_code",
        "has_completed_lpa",
        "completed_lpa",
        "has_completed_will",
        "completed_will",
        "has_uncompleted_order",
        "number_of_uncompleted_orders",
        "number_of_completed_orders",
        "number_of_orders",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email", "last_login")

    def referral_code(self, obj):
        return obj.get_or_create_referral_discount()

    def has_completed_lpa(self, obj):
        return obj.has_completed_order("LPA") > 0

    has_completed_lpa.boolean = True

    def completed_lpa(self, obj):
        return obj.has_completed_order("LPA")

    def has_completed_will(self, obj):
        return obj.has_completed_order("WILL") > 0

    has_completed_will.boolean = True

    def completed_will(self, obj):
        return obj.has_completed_order("WILL")


admin.site.register(WillCraftUser, WillCraftUserAdmin)
