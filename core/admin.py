import traceback

from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html

from services.email.email_utils import SendEmailHelper

from .serializers import OrderJsonSerializer
from .models import *

# Register your models here.


class WillOrderRepoAdmin(admin.ModelAdmin):
    search_fields = ["order__user__email", "order__order_number"]

    list_display = [
        "id",
        "order_number",
        "user",
        "user_id_number",
        "type",
        "will",
        "version",
        "downloaded",
    ]

    def user(self, obj):
        return obj.order.user

    def user_id_number(self, obj):
        return obj.order.user.personal_details.id_number

    def order_number(self, obj):
        return obj.order.order_number


admin.site.register(WillRepo, WillOrderRepoAdmin)


class OrderAdmin(admin.ModelAdmin):
    # inlines = ['RepoInline', 'RefundInline']
    list_display = [
        "user",
        "user_id_number",
        "id",
        "order_number",
        "been_paid",
        "base_discounts",
        "account_actions",
    ]
    search_fields = ["user__email"]
    readonly_fields = ("account_actions",)

    def base_discounts(self, obj):
        return obj.invoice.latest('id').discounts.all()

    def user_id_number(self, obj):
        return obj.user.personal_details.id_number if obj.user.personal_details else 0

    def been_paid(self, obj):
        return not not obj.invoice.latest_paid()

    def send_test_successs_email(self, request, order_pk, *args, **kwargs):
        order = WillOrder.objects.get(id=order_pk)
        order_json = OrderJsonSerializer(
            order, context={"show_display": True}).json
        try:
            with transaction.atomic():
                order.success(order_json)
                self.message_user(
                    request, f"Success Test Email Sent for {order.user.email}"
                )
        except Exception as e:
            messages.error(
                request, f"Success Test Email Failed for {order.user.email}: " + str(
                    e)
            )
            messages.error(
                request, "".join(traceback.format_exception(
                    None, e, e.__traceback__))
            )

        url = reverse(
            "admin:core_willorder_changelist", current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(url)

    def send_successs_email(self, request, order_pk, *args, **kwargs):
        order = WillOrder.objects.get(id=order_pk)
        try:
            with transaction.atomic():
                SendEmailHelper(order=order).send_success_email()
                SendEmailHelper(order=order).send_lawyer_email()
                self.message_user(
                    request, f"Success Email Sent for {order.user.email}")
        except Exception as e:
            messages.error(
                request, f"Success Email Failed for {order.user.email}: " + str(
                    e)
            )
            messages.error(
                request, "".join(traceback.format_exception(
                    None, e, e.__traceback__))
            )

        url = reverse(
            "admin:core_willorder_changelist", current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(url)

    def create_will(self, request, order_pk, *args, **kwargs):
        order = WillOrder.objects.get(id=order_pk)
        invoice = order.invoice.latest()
        try:
            if not invoice.been_paid:
                raise ValueError("Invoice has not been paid.")
            order.get_order_pdf(create=True)
            self.message_user(request, f"Order Created {order.user.email}")
        except Exception as e:
            messages.error(
                request, f"Order Creation Failed for {order.user.email}: " + str(
                    e)
            )
            messages.error(
                request, "".join(traceback.format_exception(
                    None, e, e.__traceback__))
            )

        url = reverse(
            "admin:core_willorder_changelist", current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(url)

    def update_invoice(self, request, order_pk, *args, **kwargs):
        order = WillOrder.objects.get(id=order_pk)
        try:
            invoice = order.invoice.latest()
            invoice.been_paid = True
            # passing update_fields of been_paid to trigger signal
            invoice.save(update_fields=["been_paid",
                                        "date_paid", "expiry_date"])
            self.message_user(
                request, f"Invoice Updated for {order.user.email}")
        except Exception as e:
            messages.error(
                request, f"Invoice Update Failed for {order.user.email}: " + str(
                    e)
            )
            messages.error(
                request, "".join(traceback.format_exception(
                    None, e, e.__traceback__))
            )

        url = reverse(
            "admin:core_willorder_changelist", current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(url)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<str:order_pk>/send_test_success_email/",
                self.admin_site.admin_view(self.send_test_successs_email),
                name="send-test-success-email",
            ),
            path(
                "<str:order_pk>/send_success_email/",
                self.admin_site.admin_view(self.send_successs_email),
                name="send-success-email",
            ),
            path(
                "<str:order_pk>/create_will/",
                self.admin_site.admin_view(self.create_will),
                name="create-will",
            ),
            path(
                "<str:order_pk>/update_invoice/",
                self.admin_site.admin_view(self.update_invoice),
                name="update-invoice",
            ),
        ]
        return custom_urls + urls

    def account_actions(self, obj):
        order = obj
        invoice = obj.invoice.latest_paid()
        return format_html(
            '<a class="button" href="{}">Send Test Success Email</a>&nbsp;'
            '<a class="button" href="{}">Send Success Email</a>&nbsp;'
            '<a class="button" href="{}">Create Order Pdf</a>&nbsp;'
            '<a class="button" href="{}">Update Invoice</a>&nbsp;'
            '<a class="button" href="{}">See Latest Order Pdf</a>',
            reverse("admin:send-test-success-email", args=[obj.pk]),
            reverse("admin:send-success-email", args=[obj.pk]),
            reverse("admin:create-will", args=[obj.pk]),
            reverse("admin:update-invoice", args=[obj.pk]),
            obj.will_repo.download_url(),
        )

    account_actions.short_description = "Account Actions"
    account_actions.allow_tags = True


admin.site.register(WillOrder, OrderAdmin)
