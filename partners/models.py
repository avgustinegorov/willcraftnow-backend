from django.contrib.auth import get_user_model
from django.db import models
from oauth2_provider.models import Application

from billing.models import DefaultDiscount
from partners.const import *

WillCraftUser = get_user_model()


class ApplicationStoreManager(models.Manager):
    def get_associated_application_store(self, user):
        try:
            return self.model.objects.get(referred_users__in=[user])
        except self.model.DoesNotExist:
            return None

    def increase_discount_applied_times(self, discounts):
        """Increase applied discount count for auto discount partners."""
        for discount in discounts:
            try:
                referred_application_store = discount.issued_by_application.application_store
                referred_application_store.discount_applied_times += 1
                referred_application_store.save()
            except (ApplicationStore.DoesNotExist, Application.DoesNotExist, AttributeError):
                pass

    def get_default_discount(self, application_store):
        if not application_store:
            return None
        try:
            # Find default discount for the partner.
            default_disc = DefaultDiscount.objects.get(
                application=application_store.application
            )
        except DefaultDiscount.DoesNotExist:
            return None
        except Application.DoesNotExist:
            return None

        return default_disc


class ApplicationStore(models.Model):
    application = models.OneToOneField(
        Application, on_delete=models.CASCADE,
        related_name='application_store'
    )

    partner = models.ForeignKey(
        "Partners", on_delete=models.CASCADE,
        related_name='application_stores'
    )

    referred_users = models.ManyToManyField(
        WillCraftUser, blank=True, related_name="referred_users"
    )

    discount_applied_times = models.SmallIntegerField(default=0)

    objects = ApplicationStoreManager()


class PartnersManager(models.Manager):
    def get_associated_partner(self, user):
        try:
            return self.model.objects.get(application_stores__referred_users__in=[user])
        except self.model.DoesNotExist:
            return None


class Partners(models.Model):
    name = models.CharField(max_length=120, unique=True, blank=False)
    logo = models.ImageField(null=True)

    agents = models.ManyToManyField(
        WillCraftUser, blank=True, related_name="agents")
    managers = models.ManyToManyField(
        WillCraftUser, blank=True, related_name="managers"
    )

    objects = PartnersManager()

    def __str__(self):
        return self.name  # pragma: no cover
