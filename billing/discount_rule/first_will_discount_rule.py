from billing.decorators import register_discount_rule
from billing.discount_rule.discount_rule import DiscountRule
from billing.models import Discount
from core.enums import LPA_ORDER, WILL_ORDER
from partners.models import ApplicationStore


@register_discount_rule()
class FirstLPADiscountRule(DiscountRule):
    slug = 'first_lpa'
    name = 'First LPA After First Will Discount Rule'

    order_type = LPA_ORDER

    @classmethod
    def apply_discount(cls, user, invoice) -> None:
        # check for cached value
        if not cls.referred_application_store:
            cls.referred_application_store = ApplicationStore.objects.get_associated_partner(
                user)
        discount, _ = Discount.objects.get_or_create_discount(
            discount_category="PARTNER_DISCOUNT",
            application=cls.referred_application_store.application,
            user=user,
        )
        print(discount)
        print(invoice.discounts.all())
        invoice.discounts.add(discount)
        invoice.update_invoice()
        invoice.save()

    @classmethod
    def check_restrictions(cls, referred_application_store, user, order_type):
        """Check restrictions for Auto Discount type of partners."""
        default_disc = ApplicationStore.objects.get_default_discount(
            referred_application_store)
        if default_disc is None:
            return False
        # This is a restriction for auto-discount company.
        # Only apply if has completed Will and discount is not applied more the restriction count.
        if (
                user.has_completed_order(WILL_ORDER)
                and order_type == cls.order_type
                and not user.has_completed_order(cls.order_type)
        ):
            return True

        return False

    @classmethod
    def can_user_have_access(cls, user, invoice) -> bool:
        # For the specific types of partners automatically create a discount.
        cls.referred_application_store = ApplicationStore.objects.get_associated_application_store(
            user)
        return bool(
            cls.referred_application_store
            and cls.check_restrictions(
                cls.referred_application_store,
                user, invoice.order.order_type
            )
        )
