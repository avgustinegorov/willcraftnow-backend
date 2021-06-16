from django.contrib import admin
from django.shortcuts import reverse
from django.utils.html import format_html

from .models import *


# Register your models here.
# c_v_uy@yahoo.com
class OrderRelatedClassAdminBase(admin.ModelAdmin):
    search_fields = ["user__email"]

    list_display = ["user_email"]

    def user_email(self, obj):
        return obj.user.email

    # Allows column order sorting
    user_email.admin_order_field = "user__email"


class AllocationAdmin(admin.ModelAdmin):
    search_fields = ["asset__order__user__email", "asset__order__order_number"]

    list_display = [
        "id",
        "user_email",
        "order_number",
        "allocated_asset",
        "allocation",
        "parent_allocation",
        "created_at",
    ]

    def allocation(self, obj):
        if obj.allocation_percentage:
            return (
                f"{obj.allocation_percentage}% ({obj.effective_allocation_percentage}%)"
            )
        elif obj.allocation_amount:
            return f"${obj.allocation_amount} (${obj.effective_allocation_amount})"
        else:
            return "No Allocation"

    def allocated_asset(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse(
                f"admin:assets_{obj.asset_store.asset.asset_type.lower()}_change",
                args=(obj.asset_store.asset.id,),
            ),
            obj.asset_store.asset.__str__(),
        )

    allocated_asset.short_description = "Asset"

    def user_email(self, obj):
        return obj.asset_store.order.user.email

    def order_number(self, obj):
        return obj.asset_store.order.order_number

    # Allows column order sorting
    user_email.admin_order_field = "asset__order__user__email"
    order_number.admin_order_field = "asset__order__order_number"


admin.site.register(Allocation, AllocationAdmin)


class AssetAdmin(OrderRelatedClassAdminBase):

    list_display = ["asset", "created_at", "check_asset_inheritance"]

    def check_asset_inheritance(self, obj):
        asset_type = obj.asset_type.lower()
        try:
            return getattr(obj, asset_type)
        except:
            return None

    def asset(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse(f"admin:assets_{obj.asset_type.lower()}_change", args=(obj.id,)),
            obj.__str__(),
        )

    # Filtering on side - for some reason, this works
    list_filter = ["asset_type"]


class AssetStoreAdmin(admin.ModelAdmin):
    search_fields = ["order__user__email"]
    list_display = ["asset", "order", "allocation"]

    def allocation(self, obj):
        total_allocation = sum(
            [
                value["allocation_percentage"]
                for value in obj.allocation.values("allocation_percentage")
                if value["allocation_percentage"]
            ]
        )
        allocations = obj.allocation.all()

        allocations_html_array = [
            f"{len(allocations)} Allocations - {total_allocation}%"
        ]
        for allocation in allocations:
            allocations_html_array += [
                'Beneficiary: <a href="{}">{}</a> Allocation: <a href="{}">{}</a>'
            ]
        allocations_html = ["<br>".join(allocations_html_array)]

        for allocation in allocations:
            allocations_html += [
                reverse(f"admin:assets_allocation_change", args=(allocation.id,)),
                allocation.__str__(entity=True),
                reverse(
                    f"admin:persons_person_change", args=(allocation.entity.id,)
                ),
                allocation.__str__(allocation=True),
            ]
        if allocations_html:
            return format_html(*allocations_html)


admin.site.register(AssetStore, AssetStoreAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(BankAccount)
admin.site.register(Company)
admin.site.register(Insurance)
admin.site.register(Investment)
admin.site.register(RealEstate)


class ResidualAdmin(admin.ModelAdmin):
    list_display = ["user", "number_orders", "number_store"]

    def number_store(self, obj):
        return [x.id for x in obj.asset_store.all()]

    def number_orders(self, obj):
        user = obj.user
        return Residual.objects.filter(user=user).count()


admin.site.register(Residual, ResidualAdmin)
