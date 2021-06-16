
from django.conf import settings
from decimal import Decimal


def cache(handle):
    def decorator(function):
        def wrapper(*args, **kwargs):
            cls = args[0]
            if not hasattr(cls, handle):
                result = function(*args, **kwargs)
                setattr(cls, handle, result)
                return result
            return getattr(cls, handle)
        return wrapper
    return decorator


class InvoiceService(object):

    addon_text = {
        "EXECUTOR": "Executor",
        "SUB_EXECUTOR": "Substiute Executor",
        "GUARDIAN": "Testamentary Guardian",
        "SUB_GUARDIAN": "Substiute Guardian",
        "BENEFICIARY": "Beneficiary/Substitute Beneficiary",
        "CHARITY_BENEFICIARY": "Charity Beneficiary",
        "ALLOCATION": "Allocation",
        "SUB_ALLOCATION": "Substitute Allocation",
        "LASTRITE": "Wishes for Last Rites",
        "INSTRUCTION": "Instructions for Dealing with Ashes",
        "DONEE": "Donee",
        "REPLACEMENT_DONEE": "Replacement Donee",
        "PROPERTY_RESTRICTION": "Restriction on Sale of Property",
        "GIFTING_RESTRICTION": "Restriction on Cash Gift Amount",
    }

    def __init__(self, order):
        self.order = order
        self.invoice = order.invoice.latest()
        self.order_type = self.order.order_type

    def quantize_price(self, price):
        return Decimal(price).quantize(Decimal(".01")) if price > 0 else 0

    @property
    @cache('_order_details')
    def order_details(self):
        entities = self.order.entitystore_set.all()
        if self.order_type == "WILL":
            return {
                "EXECUTOR": len(entities.filter_entity_type("EXECUTOR")),
                "SUB_EXECUTOR": len(entities.filter_entity_type("SUB_EXECUTOR")),
                "GUARDIAN": len(entities.filter_entity_type("GUARDIAN")),
                "SUB_GUARDIAN": len(entities.filter_entity_type("SUB_GUARDIAN")),
                "ALL_BENEFICIARY": len(entities.filter_entity_type("BENEFICIARY")),
                "BENEFICIARY": len(entities.filter_entity_type("BENEFICIARY").filter(entity_details__entity_type="Person")),
                "CHARITY_BENEFICIARY": len(entities.filter_entity_type("BENEFICIARY").filter(entity_details__entity_type="Charity")),
                "ALLOCATION": self.order.asset_store.main_allocations().count(),
                "SUB_ALLOCATION": self.order.asset_store.sub_allocations().count(),
                "INSTRUCTION": 1 if hasattr(self, "instructions") else 0,
                "LASTRITE": 1 if hasattr(self, "last_rites") else 0,
                "WITNESSES": 1 if len(entities.filter_entity_type("WITNESS")) == 2 or self.order.legal_services_witnessservice.exists() else 0
            }

        if self.order_type == "LPA":
            return {
                "DONEE": len(entities.filter_entity_type("DONEE")),
                "REPLACEMENT_DONEE": len(entities.filter_entity_type("REPLACEMENT_DONEE")),
                "PROPERTY_RESTRICTION": 1 if hasattr(self, "property_and_affairs_restrictions") and self.order.property_and_affairs_restrictions.power_to_sell_property == 'YES' else 0,
                "GIFTING_RESTRICTION": 1 if hasattr(self, "property_and_affairs_restrictions") and self.order.property_and_affairs_restrictions.power_to_give_cash == 'YES' else 0,
                "CERTIFICATE": 1 if self.order.legal_services_witnessservice.exists() else 0
            }
        if self.order_type == "SCHEDULE_OF_ASSETS":
            return {}

    @property
    @cache('_limit_details')
    def limit_details(self):
        limit_schema = {
            'WILL': ["EXECUTOR",
                     "SUB_EXECUTOR",
                     "GUARDIAN",
                     "SUB_GUARDIAN",
                     "BENEFICIARY",
                     "CHARITY_BENEFICIARY",
                     "ALLOCATION",
                     "SUB_ALLOCATION",
                     "INSTRUCTION",
                     "LASTRITE"],
            'LPA': ["DONEE",
                    "REPLACEMENT_DONEE",
                    "PROPERTY_RESTRICTION",
                    "GIFTING_RESTRICTION"],
            'SCHEDULE_OF_ASSETS':  []
        }

        order_limit_schema = limit_schema[self.order_type]

        return {key: value for (key, value) in self.order_details.items() if key in order_limit_schema}

    def validate(self):
        validation_schema = {
            'WILL': {"EXECUTOR": 1, "WITNESSES": 1, "ALL_BENEFICIARY": 1},
            "LPA": {"DONEE": 1, "CERTIFICATE": 1},
            "SCHEDULE_OF_ASSETS": {}
        }

        is_validated = True
        for key, min_limit in validation_schema[self.order_type].items():
            if not self.order_details[key] >= min_limit:
                is_validated = False
                raise Exception(
                    f"{self.order.order_number}: Validation Failed for {key}:{self.order_details[key]}")

        return is_validated

    @cache('_discounts')
    def get_discounts(self):
        return self.invoice.discounts.all()

    def get_package(self, order_details):
        all_package_names = [
            package_name for package_name in settings.PACKAGES[self.order_type]
        ]
        selected_package_name = all_package_names[0]
        for count, package_name in enumerate(all_package_names):
            package_items = settings.PACKAGES[self.order_type][package_name]["INCLUDED"]
            for item in order_details:
                if item in package_items and order_details[item] > package_items[item]:
                    selected_package_name = all_package_names[count + 1]

        selected_package = settings.PACKAGES[self.order_type][selected_package_name]
        selected_package['NAME'] = selected_package_name

        return selected_package

    @property
    @cache('_package')
    def package(self):
        return self.get_package(self.order_details)

    @property
    @cache('_prev_package')
    def previous_package(self):

        previous_invoice = self.order.invoice.previous()

        if not previous_invoice:
            return None

        order_limit = previous_invoice.order_limit.all().values("detail", "limit")

        order_details = {}
        for entry in order_limit:
            order_details[entry["detail"]] = entry["limit"]
        return self.get_package(order_details)

    @property
    @cache('_base_price')
    def base_price(self):
        base_price = Decimal(self.package["PRICE"])
        if self.invoice.is_amended_invoice():
            price_difference = Decimal(self.package["PRICE"]) - Decimal(
                self.previous_package["PRICE"]
            )
            base_price = price_difference if price_difference > 0 else 0
        return base_price

    @property
    @cache('_added_services')
    def added_services(self):
        if self.invoice.is_amended_invoice():
            return None

        service_schema = {
            "WITNESS": getattr(self.order, "legal_services_witnessservice"),
            "REVIEW": getattr(self.order, "legal_services_reviewservice"),
            "CERTIFICATE": getattr(
                self.order, "legal_services_lpacertificateservice")
        }

        language_schema = {
            "EN": 'ENGLISH',
            "CN": 'CHINESE'
        }

        result = {}

        for service_key, service in service_schema.items():
            if service.exists():
                instance = service.latest('id')
                result = {
                    "services": f"{language_schema[instance.review_type]}_{service_key}",
                    "firm": instance.firm
                }

        return result

    @property
    @cache('_services_price')
    def services_price(self):
        added_services = self.added_services
        if added_services and added_services["firm"]:
            services_price = settings.SERVICES[added_services["services"]]
            if added_services["firm"].has_gst_number:
                services_price += services_price * 7 / 100
            return services_price
        else:
            return 0

    @property
    @cache('_gross_price')
    def gross_price(self):
        return self.base_price + self.services_price

    @property
    @cache('_nett_price_and_total_discount')
    def nett_price_and_total_discount(self):
        # Creating a dictionary for code reduction in the discount loop
        prices = {"WILL_PRICE": self.base_price,
                  "SERVICES_PRICE": self.services_price}

        # Taking out discounts from the price
        discounts = self.get_discounts().values(
            "discount_type", "discount_target", "discount_amount"
        )

        total_discounted_amount = 0
        for discount in discounts:
            if discount["discount_target"] != "FULL_PRICE":
                if discount["discount_type"] == "PERCENTAGE":
                    _discount = prices[discount["discount_target"]] * (
                        discount["discount_amount"] / Decimal(100.0)
                    )

                    prices[discount["discount_target"]] -= _discount
                    total_discounted_amount += _discount
                elif discount["discount_type"] == "FIXED_PRICE":
                    prices[discount["discount_target"]
                           ] -= discount["discount_amount"]
                    total_discounted_amount += discount["discount_amount"]
            if discount["discount_target"] == "FULL_PRICE":
                if discount["discount_type"] == "PERCENTAGE":
                    _will_discount = prices["WILL_PRICE"] * (
                        discount["discount_amount"] / Decimal(100.0)
                    )
                    _service_discount = prices["SERVICES_PRICE"] * (
                        discount["discount_amount"] / Decimal(100.0)
                    )

                    prices["WILL_PRICE"] -= _will_discount
                    total_discounted_amount += _will_discount
                    prices["SERVICES_PRICE"] -= _service_discount
                    total_discounted_amount += _service_discount
                elif discount["discount_type"] == "FIXED_PRICE":
                    if discount["discount_amount"] >= prices["WILL_PRICE"]:
                        remaining_discount_amount = (
                            discount["discount_amount"] - prices["WILL_PRICE"]
                        )
                        prices["WILL_PRICE"] = 0
                        prices["SERVICES_PRICE"] -= remaining_discount_amount
                    else:
                        prices["WILL_PRICE"] -= discount["discount_amount"]
                    total_discounted_amount += discount["discount_amount"]

        # Adding the net price on the instance
        net_price = sum(prices.values())
        return net_price, total_discounted_amount

    @property
    @cache('_nett_price')
    def nett_price(self):
        nett_price, _ = self.nett_price_and_total_discount
        return nett_price

    @property
    def nett_price_after_card_fees(self):
        return self.nett_price if self.nett_price == 0 else (Decimal(self.nett_price) + Decimal(0.5)) / Decimal(1 - 3.4 / 100)

    @property
    def card_fees(self):
        return 0 if self.nett_price == 0 else self.nett_price_after_card_fees - self.nett_price

    @property
    @cache('_total_discount')
    def total_discount(self):
        _, total_discounted_amount = self.nett_price_and_total_discount
        return total_discounted_amount

    @property
    def base_lineitem(self):
        # getting line items
        base_line_items = {
            "name": (
                f"DIY {self.order.get_order_type_display()} Drafting Services -"
                f" {self.package['NAME']} {'(Upgrade)' if self.invoice.is_amended_invoice() else ''}"
            ),
            "price": self.base_price,
            "gst": None,
            "subparagraph": [],
        }

        for item, amount in self.order_details.items():
            if item in self.addon_text:
                if (amount > 0 and item in self.package["INCLUDED"]) or (
                    len(self.package["INCLUDED"]) == 0 and amount > 0
                ):
                    if item != "LASTRITE" or item != "INSTRUCTION":
                        pluralize = "Appointments" if amount > 1 else "Appointment"
                        f"- {amount} {pluralize} "
                    base_line_items["subparagraph"].append(
                        {
                            "name": f"{amount} X {self.addon_text[item]} (Included)",
                            "price": "Free",
                        }
                    )

        return base_line_items

    @property
    def services_lineitem(self):
        added_services = self.added_services

        if not added_services:
            return []

        service_text = {
            "ENGLISH_CERTIFICATE": "Certificate Issuer and english review of LPA",
            "CHINESE_CERTIFICATE": "Certificate Issuer and chinese review of LPA",
            "ENGLISH_WITNESS": "Witnessing and english review of Will",
            "CHINESE_WITNESS": "Witnessing and chinese review of Will",
            "ENGLISH_REVIEW": "English Review of Will",
            "CHINESE_REVIEW": "Chinese Review of Will",
        }

        services_lineitem = {
            "name": f"Professional Fees to {added_services['firm'].name}",
            "price": self.quantize_price(self.services_price),
            "gst": "(Inc 7% GST)" if added_services["firm"].has_gst_number else None,
            "subparagraph": [],
        }

        services_lineitem["subparagraph"].append(
            {
                "name": f"1 X {service_text[added_services['services']]}",
                "price": settings.SERVICES[added_services["services"]],
            }
        )

        services_lineitem["subparagraph"].append(
            {
                "name": f"*Collected On Behalf of {added_services['firm'].name}",
                "price": Decimal(0.00),
            }
        )

        return services_lineitem

    @property
    def edittime_lineitem(self):
        edittime_lineitem = {
            "name": "Edit Time",
            "price": self.quantize_price(0.00),
            "gst": None,
            "subparagraph": [
                {"name": f"{self.invoice.expiry_time} Days*",
                    "price": Decimal(0.00)}
            ],
        }

        return edittime_lineitem

    @property
    def discount_lineitem(self):
        discounts = self.get_discounts()

        if discounts:
            discount_lineitem = {
                "name": "Discounts",
                "price": -self.quantize_price(self.total_discount),
                "gst": None,
                "subparagraph": [],
            }

            for discount in discounts:
                discount_amount_parse = (
                    f"${discount.discount_amount}"
                    if discount.discount_type == "FIXED_PRICE"
                    else f"{discount.discount_amount}%"
                )
                discount_lineitem["subparagraph"].append(
                    {
                        "name": (
                            f"{discount_amount_parse} Off (Code:"
                            f" {discount.discount_code})"
                        ),
                        "price": Decimal(0.00),
                    }
                )
            return discount_lineitem
        else:
            return None

    def append_lineitems(self, value):
        if not hasattr(self, "_lineitems"):
            setattr(self, "_lineitems", [])
        if value:
            self._lineitems.append(value)

    def get_line_items(self):
        setattr(self, "_lineitems", [])
        self.append_lineitems(self.base_lineitem)
        self.append_lineitems(self.services_lineitem)
        self.append_lineitems(self.edittime_lineitem)
        self.append_lineitems(self.discount_lineitem)
        return getattr(self, "_lineitems")
