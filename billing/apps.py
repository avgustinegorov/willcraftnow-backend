from django.apps import AppConfig


class BillingConfig(AppConfig):
    name = "billing"

    def ready(self):
        import billing.signals
        import billing.discount_rule.first_will_discount_rule
