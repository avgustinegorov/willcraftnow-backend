import datetime

import stripe
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import WillOrder
from core.permissions import BaseOrderPermission
from partners.models import ApplicationStore
from services.pdf_gen.invoice_generator import invoice_generator

from .models import CustomerBilling, Invoice
from .serializers import DiscountSerializer, InvoiceSerializer
from core.serializers import OrderJsonSerializer


class CreateDiscountView(APIView):
    """ view to create discounts """

    permission_classes = (BaseOrderPermission,)
    serializer_class = DiscountSerializer

    def post(self, request, order_pk, format=None):
        serializer = DiscountSerializer(
            data=request.data, context={"order": order_pk})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )  # pragma: no cover


class RetrieveUpdateInvoiceView(generics.RetrieveAPIView):  # pragma: no cover
    """A Generic RETRIEVE/UPDATE View that returns the Order's Invoice
    This is mainly used for DEVELOPMENT

    endpoint: /billing/<order_pk>/invoice/

    get: Returns a detailed representation of the Order's Invoice

    put: Update the Order's Invoice with the data provided in the request's body

    patch: Partially update the Order's Invoice with the data provided in the request's body
    """

    serializer_class = InvoiceSerializer
    permission_classes = (BaseOrderPermission,)

    def get_object(self):
        """ Returns the invoice related to the given order """
        order = get_object_or_404(WillOrder, id=self.kwargs["order_pk"])
        return order.invoice.latest()


class StripeOneOffChargeView(APIView):
    """A Custom APIView that charges the user"""

    permission_classes = (BaseOrderPermission,)

    def get(self, request, order_pk):  # pragma: no cover
        return Response({"exists": "yes!"}, status=200)

    def post(self, request, order_pk):
        """Transfers all of the token's
        orders to the logged in user
        """

        order = WillOrder.objects.get(id=order_pk)
        order_json = OrderJsonSerializer(
            order, context={"show_display": True}).json
        # updating invoice
        invoice = order.invoice.latest()
        invoice = invoice.update_invoice()

        # get net price after card fees to charge
        net_price_after_card_fees = invoice.net_price_after_card_fees
        net_price = invoice.net_price

        if net_price > 0:
            # getting token from request
            try:
                token = request.data["body"]
            except:
                return Response(
                    {"message": "Please include a token for payments more than $0."}
                )

            # stripe payments
            try:
                # change in production
                stripe.api_key = settings.STRIPE_SECRET

                if not CustomerBilling.objects.filter(user=request.user).exists():
                    # Create a Customer:
                    customer = stripe.Customer.create(
                        source=token, email=request.user.email,
                    )
                    CustomerBilling.objects.create(
                        user=request.user, customer_token=customer.id
                    )
                else:
                    customer_id = CustomerBilling.objects.get(
                        user=request.user
                    ).customer_token
                    customer = stripe.Customer.retrieve(customer_id)

                charge = stripe.Charge.create(
                    amount=int(net_price_after_card_fees * 100),
                    currency="SGD",
                    customer=customer,
                    description=(
                        f"{order.order_number} Purchased on"
                        f" {str(datetime.datetime.now())}"
                    ),
                )

                with transaction.atomic():
                    invoice.been_paid = True
                    # Increase the counter of discount applied on referred partner.
                    ApplicationStore.objects.increase_discount_applied_times(
                        invoice.discounts.all())
                    # passing update_fields of been_paid to trigger signal
                    invoice.save(
                        update_fields=["been_paid", "date_paid", "expiry_date"]
                    )

                    # sending emails for success
                    invoice.order.success(order_json)
                    # SendEmailHelper(order=invoice.order).send_success_email()
                    # SendEmailHelper(order=invoice.order).send_lawyer_email()
                    # if Testing
                    # invoice.been_paid = False
                    # invoice.save(update_fields=[
                    #     "been_paid", "date_paid", "expiry_date"
                    # ])

                return Response(
                    {"message": "Payment is successful."}, status=status.HTTP_200_OK
                )

            except stripe.error.CardError as ce:
                body = ce.json_body
                body.get("error", {})
                return Response(
                    {"message": str(ce)}, status=status.HTTP_400_BAD_REQUEST
                )

        else:
            invoice.been_paid = True
            # Increase the counter of discount applied on referred partner.
            ApplicationStore.objects.increase_discount_applied_times(
                invoice.discounts.all())
            # passing update_fields of been_paid to trigger signal
            invoice.save(update_fields=["been_paid",
                                        "date_paid", "expiry_date"])

            # sending emails for success
            invoice.order.success(order_json)

            return Response(
                {"message": "It's Free! No Payment Needed."}, status=status.HTTP_200_OK
            )
