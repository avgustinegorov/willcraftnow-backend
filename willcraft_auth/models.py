from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from billing.models import Discount
from lawyer_services.models import Firm
from persons.models import Entity
# from partners.models import Partners

# Create your models here.


class WillCraftUserManager(BaseUserManager):  # pragma: no cover
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class WillCraftUser(AbstractUser):
    """A Custom User class that's also connected to the History
    Model through signals
    """

    username = None
    email = models.EmailField(_("email address"), unique=True)
    personal_details = models.OneToOneField(
        "persons.Person",
        on_delete=models.SET_NULL,
        null=True,
        related_name="user_detail",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = WillCraftUserManager()

    def __str__(self):
        return self.email  # pragma: no cover

    def get_entities(self):
        return Entity.objects.filter(user=self)

    @property
    def get_user_type(self):
        if self.is_lawyer:
            return "LAWYER"
        elif self.is_superuser or self.is_staff:
            return "ADMIN"
        # elif Partners.objects.filter(agents__in=[self]).exists():
        #     return "PARTNER"
        else:
            return "USER"

    def add_user_to_partner(self, client_id=None, application=None):
        from partners.models import ApplicationStore
        # remove previous associations
        associated_applications = ApplicationStore.objects.filter(
            referred_users__in=[self]
        )
        for application_store in associated_applications:
            application_store.referred_users.remove(self)

        if application:
            try:
                application_store = application.application_store
            except ApplicationStore.DoesNotExist:
                application_store = None
        elif client_id:
            try:
                application_store = ApplicationStore.objects.get(
                    application__client_id=client_id
                )
            except ApplicationStore.DoesNotExist:
                application_store = None
        else:
            application_store = None

        if application_store:
            application_store.referred_users.add(self)

    @property
    def get_associated_firms(self):
        return self.lawyers.all()

    @property
    def is_lawyer(self):
        return True if self.get_associated_firms else False

    def get_or_create_referral_discount(self):
        return Discount.objects.get_or_create_discount(
            discount_category="REFERRAL_DISCOUNT", user=self
        )

    @property
    def last_interaction(self):
        return self.last_login if self.last_login else self.date_joined

    def has_completed_order(self, order_type=None):
        all_orders = self.user_orders.all()
        if not len(all_orders):
            return False
        else:
            paid_orders = [
                n for n in all_orders if n.invoice.latest().been_paid is True]
            if order_type:
                paid_orders = [
                    n for n in paid_orders if n.order_type == order_type]
            return len(paid_orders)

    @property
    def has_uncompleted_order(self):
        all_orders = self.user_orders.all()
        if not len(all_orders):
            return False
        else:
            unpaid_orders = [n for n in all_orders if n.been_paid() != True]
            return not not len(unpaid_orders)

    @property
    def number_of_uncompleted_orders(self):
        all_orders = self.user_orders.all()
        if not len(all_orders):
            return "No Orders"
        else:
            unpaid_orders = [n for n in all_orders if n.been_paid() != True]
            return len(unpaid_orders)

    @property
    def number_of_completed_orders(self):
        all_orders = self.user_orders.all()
        if not len(all_orders):
            return "No Orders"
        else:
            paid_orders = [n for n in all_orders if n.been_paid() == True]
            return len(paid_orders)

    @property
    def number_of_orders(self):
        return self.user_orders.count()

    def save(self, *args, **kwargs):
        """ creates a discount when registering user """
        with transaction.atomic():
            super().save(*args, **kwargs)
            self.get_or_create_referral_discount()
