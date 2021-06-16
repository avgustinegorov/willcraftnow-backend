from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files import File
from oauth2_provider.models import Application

from billing.models import DefaultDiscount, Discount
from content.models import *
from content.models import FAQ, TipsKeyWords
from lawyer_services.models import Firm
from partners.models import ApplicationStore, Partners
from persons.models import EntityType
from willcraft_auth.models import WillCraftUser


def run(*args):
    if "setup" in args:
        print("Running Setup")
        SetSite()
        CreateSuperUser()
        CreateApplication()
        CreateOtherApplication()
        CreateTips()
        CreateFAQs()
        CreateReferralPartner()
        CreateEntityTypes()
        PortReferalDiscount()
        # CreateDefaultDiscountTypes()
        CreateFirms()

    else:
        print("Running All")
        SetSite()
        CreateSuperUser()
        CreateApplication()
        CreateOtherApplication()
        CreateTips()
        CreateFAQs()
        CreateReferralPartner()
        CreateEntityTypes()
        # CreateDefaultDiscountTypes()
        CreateFirms()


def CreateReferralPartner():
    if not Partners.objects.filter(name="test_referral").exists():
        user = WillCraftUser.objects.get(email="admin@example.com")
        application = Application.objects.create(
            user=user,
            client_type="public",
            authorization_grant_type="password",
            name="test_application",
        )
        partner = Partners.objects.create(
            name="test_referral")
        logo_file_path = os.path.join(
            settings.BASE_DIR, f"scripts/placeholder_logo.png"
        )

        with open(logo_file_path, "rb") as doc_file:
            partner.logo.save(
                "placeholder_logo.png", File(doc_file), save=True
            )

        application_store = ApplicationStore.objects.create(
            application=application, partner=partner)

        application_store.referred_users.add(user)

        DefaultDiscount.objects.create(application=application)


def CreateApplication():
    try:
        user = WillCraftUser.objects.get(email="admin@example.com")
        if not Application.objects.filter(name="WillCraft").exists():
            application = Application.objects.create(
                user=user,
                client_type="public",
                authorization_grant_type="password",
                name="WillCraft",
            )
            partner = Partners.objects.create(
                name="WillCraft")
            ApplicationStore.objects.create(
                application=application, partner=partner)
        else:
            if not Partners.objects.filter(name="WillCraft").exists():
                application = Application.objects.get(name="WillCraft")
                partner = Partners.objects.get(
                    name="WillCraft")
                ApplicationStore.objects.create(
                    application=application, partner=partner)

    except:
        pass


def CreateOtherApplication():
    try:
        user = WillCraftUser.objects.get(email="admin@example.com")
        if not Application.objects.filter(name="OtherTestApp").exists():
            application = Application.objects.create(
                user=user,
                client_type="public",
                redirect_uris="https://127.0.0.1/success/",
                authorization_grant_type="authorization-code",
                name="OtherTestApp",
            )
            partner = Partners.objects.create(
                name="OtherTestApp")
            ApplicationStore.objects.create(
                application=application, partner=partner)
        else:
            if not Partners.objects.filter(name="OtherTestApp").exists():
                application = Application.objects.get(name="OtherTestApp")
                partner = Partners.objects.get(name="OtherTestApp")
                ApplicationStore.objects.create(
                    application=application, partner=partner)
    except:
        pass


def SetSite():
    try:
        current_site = Site.objects.get(domain="example.com")
        current_site.domain = "willcraftnow-staging.herokuapp.com"
        current_site.display_name = "willcraftnow-staging.herokuapp.com"
        current_site.save()
    except:
        pass


def CreateSuperUser():
    try:
        WillCraftUser.objects.create_superuser(
            "admin@example.com", "adminpass")
    except:
        pass


def CreateFirms():

    try:
        if not Firm.objects.all():
            FIRMS = [
                ("Firm1", "Firm 1"),
                ("Firm2", "Firm 2"),
            ]

            for firm in FIRMS:
                if not Firm.objects.filter(name=firm[0]).exists():
                    email = f"{firm[0]}@{firm[0]}.com"
                    firm_instance = Firm.objects.create(
                        name=firm[0], email=email)

                    tncs_file_path = os.path.join(
                        settings.BASE_DIR, f"scripts/{firm[0]}_tncs.pdf"
                    )

                    with open(tncs_file_path, "rb") as doc_file:
                        firm_instance.tncs_file.save(
                            f"{firm[0]}_tncs.pdf", File(doc_file), save=True
                        )
    except:
        pass


def CreateDefaultDiscountTypes():

    DISCOUNT_REDUCTION_TYPES = [
        # Percent discount from the reduction target
        ("PERCENTAGE", "Percent Discount",),
        # Percent discount of a fixed price from total
        ("FIXED_PRICE", "Fixed Price Discount",),
    ]

    REDUCTION_TARGET_CHOICES = [
        ("WILL_PRICE", "Will Price Discount",),  # Discount from the will price
        # Discount from all of the services price(s)
        ("SERVICES_PRICE", "Service Price Discount",),
    ]

    try:

        for discount_reduction_type in DISCOUNT_REDUCTION_TYPES:
            for reduction_target in REDUCTION_TARGET_CHOICES:
                discount_amount = 10
                discount_target = reduction_target[0]
                discount_type = discount_reduction_type[0]
                is_active = True
                discount_code = f"{discount_target}_{discount_type}_{discount_amount}"
                if not Discount.objects.filter(discount_code=discount_code).exists():
                    Discount.objects.create(
                        discount_amount=discount_amount,
                        discount_target=discount_target,
                        discount_type=discount_type,
                        is_active=is_active,
                        discount_code=discount_code,
                    )
    except:
        pass


def CreateEntityTypes():

    PERSON_TYPES = [
        ("EXECUTOR", "Executor",),
        ("SUB_EXECUTOR", "Sub-Executor",),
        ("GUARDIAN", "Guardian",),
        ("SUB_GUARDIAN", "Sub-Guardian",),
        ("WITNESS", "Witness",),
        ("BENEFICIARY", "Beneficiary",),
    ]

    try:
        for type in PERSON_TYPES:
            if not EntityType.objects.filter(type_name=type[0]).exists():
                EntityType.objects.create(type_name=type[0])
    except:
        pass


def CreateTips():
    from scripts.tips import TIPS_CONST

    try:
        TipsKeyWords.objects.all().delete()

        for tip in TIPS_CONST:
            if not TipsKeyWords.objects.filter(
                order_type=tip["order_type"],
                step=tip["step"],
                tip_type=tip["tip_type"],
                title=tip["title"],
            ).exists():
                TipsKeyWords.objects.create(
                    order_type=tip["order_type"],
                    step=tip["step"],
                    tip_type=tip["tip_type"],
                    title=tip["title"],
                    content=tip["content"],
                )
    except:
        pass


def CreateFAQs():
    from scripts.faqs import FAQ_CONST

    try:
        FAQ.objects.all().delete()

        for faq in FAQ_CONST:
            if not FAQ.objects.filter(title=faq["title"]).exists():
                FAQ.objects.create(title=faq["title"], content=faq["content"])
    except:
        pass
