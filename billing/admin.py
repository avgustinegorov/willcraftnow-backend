from django.contrib import admin
from django.shortcuts import reverse
from django.utils.html import format_html

from .models import *

# Register your models here.


class InvoiceAdmin(admin.ModelAdmin):
    search_fields = ["order__user__email", "order__order_number"]
    list_display = [
        "id",
        "order_number",
        "user",
        "invoice_pdf",
        "been_paid",
        "date_paid",
        "expiry_date",
        "net_price",
        "net_price_after_card_fees",
        "card_fees",
    ]
    list_display_links = [
        "id",
        "order_number",
        "user",
    ]

    def invoice_pdf(self, obj):
        invoice_pdf = obj.invoice_repo.latest("uploaded_at").invoice_pdf
        try:
            return format_html(
                '<a href="{}">{}</a>', invoice_pdf.path, invoice_pdf.path
            )
        except:
            return format_html(
                '<a href="{}">{}</a>', invoice_pdf.name, invoice_pdf.name
            )

    def order_number(self, obj):
        order = obj.order
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:core_willorder_change", args=(order.id,)),
            order.order_number,
        )

    def user(self, obj):
        user = obj.order.user
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:willcraft_auth_willcraftuser_change", args=(user.id,)),
            obj.order.user,
        )


class InvoiceRepoAdmin(admin.ModelAdmin):
    search_fields = ["invoice__order__user__email", "invoice__order__order_number"]
    readonly_fields = ["version"]
    list_display = [
        "invoice",
        "version",
        "invoice_pdf",
        "downloaded",
    ]


class DiscountAdmin(admin.ModelAdmin):
    search_fields = ["issued_by__email", "issued_to__email"]
    list_display = [
        "discount_code",
        "discount_category",
        "redeemed",
        "max_redeemed",
        "expiry_date",
        "issued_by",
        "issued_to",
        "issued_by_application",
    ]


class DefaultDiscountAdmin(admin.ModelAdmin):
    list_display = [
        "discount_category",
        "discount_type",
        "discount_target",
        "discount_amount",
        "application",
    ]


admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(DefaultDiscount, DefaultDiscountAdmin)
admin.site.register(OrderLimit)
admin.site.register(InvoiceRepo, InvoiceRepoAdmin)
