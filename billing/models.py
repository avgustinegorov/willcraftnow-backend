import random
import string

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models, transaction
from oauth2_provider.models import Application
from services.s3.s3_interface import S3Interface

from .services import InvoiceService


def random_string_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


class CustomerBilling(models.Model):
    # this model is used with stripe to track customer tokens
    user = models.OneToOneField(
        "willcraft_auth.WillCraftUser",
        on_delete=models.CASCADE,
        null=False,
        related_name="customer",
    )
    customer_token = models.CharField(max_length=256, blank=False)


class AbstractBaseDiscount(models.Model):
    """Defines a Discount that can be applied
    to an Invoice to modify the price -
    this is applied automatically for referral discounts from the order's user
    (on order -> invoice creation) but the other discounts
    must be added to the invoice through some process
    """

    DISCOUNT_REDUCTION_TYPES = [
        # Percent discount from the reduction target
        ("NO_DISCOUNT", "No Discount",),
        # Percent discount from the reduction target
        ("PERCENTAGE", "Percent Discount",),
        # Percent discount of a fixed price from total
        ("FIXED_PRICE", "Fixed Price Discount",),
    ]

    REDUCTION_TARGET_CHOICES = [
        ("WILL_PRICE", "Will Price Discount",),  # Discount from the will price
        # Discount from all of the services price(s)
        ("SERVICES_PRICE", "Service Price Discount",),
        # Discount from all of the price(s)
        ("FULL_PRICE", "Full Discount",),
    ]
    PARTNER_DISCOUNT = "PARTNER_DISCOUNT"
    REFERRAL_DISCOUNT = "REFERRAL_DISCOUNT"
    GENERAL_DISCOUNT = "GENERAL_DISCOUNT"
    ABANDONED_CART_DISCOUNT = "ABANDONED_CART_DISCOUNT"

    DISCOUNT_CATEGORY_CHOICES = [
        (PARTNER_DISCOUNT, "Partner Discount",),
        (REFERRAL_DISCOUNT, "Referral Discount",),
        (GENERAL_DISCOUNT, "General Discount",),
        (ABANDONED_CART_DISCOUNT, "Abandoned Cart Discount",),
    ]

    discount_category = models.CharField(
        max_length=25,
        blank=False,
        choices=DISCOUNT_CATEGORY_CHOICES,
        default=REFERRAL_DISCOUNT,
    )

    discount_type = models.CharField(
        max_length=25,
        blank=False,
        choices=DISCOUNT_REDUCTION_TYPES,
        default="FIXED_PRICE",
    )

    discount_target = models.CharField(
        max_length=25,
        blank=False,
        choices=REDUCTION_TARGET_CHOICES,
        default="WILL_PRICE",
    )

    discount_amount = models.DecimalField(
        max_digits=100, decimal_places=2, null=False, default="9.90"
    )

    class Meta:
        abstract = True


class DefaultDiscountManager(models.Manager):
    """Define a model manager for User model with no username field."""

    def get_or_create_default_discount(self, application):
        try:
            return self.get(application=application)
        except self.model.DoesNotExist:
            discount_amount = 9.90
            return self.create(
                discount_type="FIXED_PRICE",
                discount_target="WILL_PRICE",
                discount_amount=discount_amount,
                application=application
            )
        except self.model.MultipleObjectsReturned:
            # cache exception for null situation
            return self.filter(application=application).first()

    def get_default_discount_values(self, application):
        default_discount = self.get_or_create_default_discount(application)
        return self.filter(id=default_discount.id).values(
            "discount_type", "discount_target", "discount_amount", "discount_category"
        )[0]


class DefaultDiscount(AbstractBaseDiscount):

    application = models.OneToOneField(
        Application,
        null=True,
        related_name="default_discount",
        on_delete=models.CASCADE
    )

    objects = DefaultDiscountManager()


class DiscountManager(models.Manager):
    def get_or_create_discount(self, user=None, application=None, discount_category=None):
        if not discount_category:
            raise Exception(
                "Please provide Discount Category kwarg"
            )  # pragma: no cover
        if not (user or application):
            raise Exception(
                "Please provide either User or Application kwarg"
            )  # pragma: no cover
        try:
            return (
                self.get(
                    discount_category=discount_category,
                    issued_by_application=application,
                    issued_to=user,
                ),
                False,
            )
        except self.model.DoesNotExist:
            return (
                self.create_discount_from_default(application),
                True,
            )
        except self.model.MultipleObjectsReturned:
            return (
                self.filter(
                    discount_category=discount_category,
                    issued_by_application=application,
                    issued_to=user,
                ).latest("id"),
                True,
            )

    def create_discount_from_default(self, application):
        discount_values = DefaultDiscount.objects.get_default_discount_values(
            application
        )
        return self.create(issued_by_application=application, **discount_values)


class Discount(AbstractBaseDiscount):
    """Defines a Discount that can be applied
    to an Invoice to modify the price -
    this is applied automatically for referral discounts from the order's user
    (on order -> invoice creation) but the other discounts
    must be added to the invoice through some process
    """

    # A unique discount code that a user can apply on an order's invoice through provided endpoints
    discount_code = models.CharField(
        max_length=526, unique=True, null=False, blank=False
    )

    redeemed = models.IntegerField(default=0, null=True, blank=True)
    redeemed_by = models.ManyToManyField(
        "willcraft_auth.WillCraftUser", null=True, blank=True
    )
    max_redeemed = models.IntegerField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)

    # comments = models.CharField(max_length=526, blank=True, null=True)

    issued_to = models.ForeignKey(
        "willcraft_auth.WillCraftUser",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="issued_to",
    )

    issued_by = models.ForeignKey(
        "willcraft_auth.WillCraftUser",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="issued_by",
    )

    issued_by_application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="issued_discounts",
    )

    # Field to toggle a discount code on/off dynamically
    is_active = models.BooleanField(default=True)

    objects = DiscountManager()

    def generate_discount_code(self, code=None):
        if not code:
            code = random_string_generator()

        while True:
            if not Discount.objects.filter(discount_code=code).exists():
                break
            code = random_string_generator()

        return code

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.discount_code:
                self.discount_code = self.generate_discount_code()

            super().save(*args, **kwargs)

    def __str__(self):
        return (  # pragma: no cover
            f"{self.discount_code} : {self.discount_type} - {self.discount_target}"
            f" ({self.discount_amount})"
        )


class OrderLimit(models.Model):
    # Auto-Now (add) fields to keep track of model changes
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    # Addon details using
    detail = models.CharField(max_length=256, blank=True)
    limit = models.IntegerField()

    # related invoice
    invoice = models.ForeignKey(
        "Invoice", on_delete=models.CASCADE, null=False, related_name="order_limit"
    )

    def __str__(self):
        return (  # pragma: no cover
            f"{self.invoice.order.order_number} ({self.detail}) ({self.limit})"
        )


class InvoiceManager(models.Manager):

    def latest(self, *args, **kwargs):
        if self.instance.__class__.__name__ == 'WillOrder':
            queryset = self.get_queryset()
            if len(queryset) == 0:
                return self.create()
            else:
                return queryset.latest(*args, **kwargs)

        return super().latest(*args, **kwargs)

    def latest_paid(self, *args, **kwargs):
        if self.instance.__class__.__name__ == 'WillOrder':
            queryset = self.get_queryset().filter(been_paid=True)
            if len(queryset) == 0:
                return None
            else:
                return queryset.latest(*args, **kwargs)
        else:
            raise Exception("Cannot call latest_paid.")

    def previous(self, *args, **kwargs):
        queryset = self.get_queryset().order_by("-id")
        if len(queryset) >= 2:
            return queryset[1]
        else:
            return None


class Invoice(models.Model):
    """A Model defining an invoice created against a
    WillOrder that contains billing details for said
    order.
    The Instance itself is created and updated alongside it's related order,
    but the `update_invoice` method can be used to update the invoice's
    fields with the related fields from the order
    """

    # Auto-Now (add) fields to keep track of model changes
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    # The Order this Invoice was created against
    order = models.ForeignKey(
        "core.WillOrder", on_delete=models.CASCADE, null=False, related_name="invoice"
    )

    parent_invoice = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )

    # The Invoice Price before discounts
    gross_price = models.DecimalField(
        default=49.90, max_digits=100, decimal_places=2)

    # The Invoice Price after discounts
    net_price = models.DecimalField(
        default=49.90, max_digits=100, decimal_places=2)

    # The Invoice Price after discounts
    net_price_after_card_fees = models.DecimalField(
        default=49.90, max_digits=100, decimal_places=2
    )

    # The Invoice Price after discounts
    card_fees = models.DecimalField(
        default=49.90, max_digits=100, decimal_places=2)

    # Discounts that were applied against this invoice to generate the cost
    discounts = models.ManyToManyField("Discount", blank=True)

    # Set to true after successful user payment
    been_paid = models.BooleanField(default=False)
    # Date and time of payment
    date_paid = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )
    expiry_time = models.IntegerField(default=7, blank=True)
    # Date and time of expiry set at the time of payment
    expiry_date = models.DateTimeField(
        auto_now=False, auto_now_add=False, blank=True, null=True, editable=False
    )

    objects = InvoiceManager()

    class Meta:
        get_latest_by = "id"

    def __str__(self):  # pragma: no cover
        type = "Original"
        if self.parent_invoice != None:
            type = "Amended"
        return (
            f"{self.order.user} {self.order.order_number} ({self.net_price}) ({type})"
        )

    def save(self, *args, **kwargs):

        if (
            self.parent_invoice is None
            and Invoice.objects.filter(order=self.order, parent_invoice=None).exists()
            and self.id == Invoice.objects.get(order=self.order, parent_invoice=None)
        ):
            raise ValidationError(
                "Cannot have more than one main Invoice!"
            )  # pragma: no cover

        super().save(*args, **kwargs)

    def is_amended_invoice(self):
        return self.parent_invoice is not None

    def update_invoice(self):
        """Receives an order model and all potential discounts as input
        and updates the invoice with the discounts applied
        """

        service = InvoiceService(self.order)

        self.gross_price = service.quantize_price(service.gross_price)
        self.net_price = service.quantize_price(service.nett_price)
        self.card_fees = service.quantize_price(service.card_fees)
        self.net_price_after_card_fees = service.quantize_price(
            service.nett_price_after_card_fees)

        return self


def get_pdf_invoice_upload_path(instance, filename):
    return f"invoice_repo/{filename}"


class InvoiceRepoManager(models.Manager):

    def next_version(self):
        latest = self.latest('id')
        version = 1
        if latest:
            version = latest.version + 1
        return version

    def next_filename(self):
        if self.instance.__class__.__name__ == 'Invoice':
            version = self.next_version()
            order_number = self.instance.order.order_number
            return f"invoice_repo/Invoice_{order_number}_v{version}.pdf"

    def upload_url(self):
        if self.instance.__class__.__name__ == 'Invoice':
            return S3Interface().get_put_presigned_url(self.next_filename())

    def download_url(self):
        if self.instance.__class__.__name__ == 'Invoice':
            latest = self.latest()
            if latest:
                if settings.STAGE != "LOCAL":
                    filename = "media/" + latest.invoice_pdf.name
                    return S3Interface().get_download_presigned_url(filename)
                else:
                    return f"/media/{latest.invoice_pdf}"

            return None

    def latest(self, *args, **kwargs):
        # this is only for the related manager instance
        # where this is called: invoice.invoice_repo.latest()
        # the instance here is a WillOrder instance
        if self.instance.__class__.__name__ == 'Invoice':
            queryset = self.get_queryset()
            if not queryset.exists():
                return None
            else:
                return queryset.latest(*args, **kwargs)

        return super().latest(*args, **kwargs)


class InvoiceRepo(models.Model):
    invoice = models.ForeignKey(
        "Invoice", on_delete=models.CASCADE, null=True, related_name="invoice_repo"
    )
    invoice_pdf = models.FileField(
        upload_to=get_pdf_invoice_upload_path, null=True)
    version = models.IntegerField(default=1)
    downloaded = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    objects = InvoiceRepoManager()

    class Meta:
        get_latest_by = ['id', 'version']

    def __str__(self):  # pragma: no cover
        return f"{self.invoice.order.order_number}_{self.version}"

    def save(self, *args, **kwargs):
        if hasattr(self, "skip_signal") and self.skip_signal:
            super(InvoiceRepo, self).save(*args, **kwargs)  # pragma: no cover
            return  # pragma: no cover

        if not self.pk:
            self.invoice_pdf = self.invoice.invoice_repo.next_filename()
            self.version = self.invoice.invoice_repo.next_version()

        super(InvoiceRepo, self).save(*args, **kwargs)
