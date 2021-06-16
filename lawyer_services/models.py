from django.db import models
from django.utils.translation import ugettext_lazy as _


def get_pdf_invoice_upload_path(self, instance):
    return f"partner_firms/{self.name}"  # pragma: no cover


class Firm(models.Model):
    """Defines a firm that can have multiple
    Lawyers linked to itself through Foreign Keys
    """

    name = models.CharField(max_length=120, blank=False,
                            verbose_name=_("Firm"))
    email = models.CharField(max_length=120, blank=False)
    description = models.TextField(blank=True)

    has_gst_number = models.BooleanField(default=False)
    tncs_file = models.FileField(
        upload_to=get_pdf_invoice_upload_path, null=True)
    contact_number = models.CharField(max_length=120, blank=True)
    lawyers = models.ManyToManyField(
        "willcraft_auth.WillCraftUser", null=True, blank=True, related_name="lawyers"
    )

    def __str__(self):
        return self.name  # pragma: no cover


class LegalServices(models.Model):
    """Defines an Abstract Asset model
    that all legal services models must inherit from
    to implement legal services that a firm may offer to a user
    """

    REVIEW_TYPE = [
        ("EN", "English Review",),
        ("CN", "Chinese Review",),
    ]

    service_type = models.CharField(
        max_length=100, default="WITNESS", blank=True)

    review_type = models.CharField(
        max_length=60, choices=REVIEW_TYPE, default="EN", blank=False
    )
    # Auto-Now (add) fields to keep track of model changes
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    # The order this asset belongs to - links all legal services directly to the order
    order = models.ForeignKey(
        "core.WillOrder",
        on_delete=models.CASCADE,
        related_name="legal_services_%(class)s",
    )
    firm = models.ForeignKey("Firm", on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def service_been_paid(self):
        """
        Used to deny delete changes when the service has been paid for.
        TODO: deny update and create changes?
        """
        latest_paid_invoice = self.order.invoice.latest_paid()
        if latest_paid_invoice == None:
            return False
        if latest_paid_invoice.date_paid > self.last_updated_at:
            return True
        else:
            return False


class WitnessService(LegalServices):
    """An legal service for witnessing
    Contains the fields generic to Legal Serices and
    fields specific to witnessing
    """

    # person_1 = models.ForeignKey("willcraft_auth.WillCraftUser",
    #                              on_delete=models.SET_NULL,
    #                              null=True,
    #                              related_name="witness_1")
    # person_2 = models.ForeignKey("willcraft_auth.WillCraftUser",
    #                              on_delete=models.SET_NULL,
    #                              null=True,
    #                              related_name="witness_2")

    def __str__(self):
        return f"{self.order}_{self.review_type}"  # pragma: no cover

    def save(self, *args, **kwargs):
        """ Updates the legal service type to witness """
        self.service_type = "WITNESS"
        super(WitnessService, self).save(*args, **kwargs)


class ReviewService(LegalServices):
    """An legal service for witnessing
    Contains the fields generic to Legal Serices and
    fields specific to witnessing
    """

    def __str__(self):
        return f"{self.order}_{self.review_type}"  # pragma: no cover

    def save(self, *args, **kwargs):
        """ Updates the legal service type to review """
        self.service_type = "REVIEW"
        super(ReviewService, self).save(*args, **kwargs)


class LPACertificateService(LegalServices):
    """An legal service for witnessing
    Contains the fields generic to Legal Serices and
    fields specific to witnessing
    """

    def __str__(self):
        return f"{self.order}_{self.review_type}"  # pragma: no cover

    def save(self, *args, **kwargs):
        """ Updates the legal service type to review """
        self.service_type = "LPA_CERTIFICATE"
        super(LPACertificateService, self).save(*args, **kwargs)
