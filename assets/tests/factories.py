import random
import string
import uuid

import factory
from core.tests import factories as core_factories
from factory.django import DjangoModelFactory
from persons.tests import factories as person_factories
from willcraft_auth.tests import factories as auth_factories

from ..models import (
    Allocation,
    Asset,
    AssetStore,
    BankAccount,
    Company,
    Insurance,
    Investment,
    RealEstate,
    Residual,
)


class AssetFactory(DjangoModelFactory):
    class Meta:
        model = Asset

    user = factory.SubFactory(auth_factories.UserFactory)


class RealEstateFactory(AssetFactory):
    class Meta:
        model = RealEstate

    asset_type = "RealEstate"

    country = "SG"
    real_estate_type = "HDB_FLAT"
    mortgage = "MORTGAGE"
    holding_type = "JOINT_TENANT"
    postal_code = str(random.randint(100000, 200000))
    floor_number = str(random.randint(1, 20))
    unit_number = str(random.randint(1, 200))
    block_number = factory.lazy_attribute(
        lambda x: "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(3)
        )
    )
    street_name = factory.lazy_attribute(
        lambda x: "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
        )
    )

    @staticmethod
    def get_params(allocations):
        return dict(
            real_estate_address=allocations[0].asset_store.asset.address,
            real_estate_postal_code=allocations[0].asset_store.asset.postal_code,
        )


class BankAccountFactory(AssetFactory):
    class Meta:
        model = BankAccount

    asset_type = "BankAccount"

    bank = factory.LazyAttribute(lambda x: str(uuid.uuid4())[:4])
    account_number = factory.LazyAttribute(lambda x: str(uuid.uuid4())[:4])

    @staticmethod
    def get_params(allocations):
        return dict(
            bank_name=allocations[0].asset_store.asset.bank,
            bank_account_number=allocations[0].asset_store.asset.account_number,
        )


class InsuranceFactory(AssetFactory):
    class Meta:
        model = Insurance

    asset_type = "Insurance"

    insurer = factory.LazyAttribute(lambda x: "INSURER-" + str(uuid.uuid4())[:4])
    plan = factory.LazyAttribute(lambda x: "PLAN-" + str(uuid.uuid4())[:4])
    policy_number = factory.LazyAttribute(lambda x: "POLICY-" + str(uuid.uuid4())[:4])

    @staticmethod
    def get_params(allocations):
        return dict(
            insurer_name=allocations[0].asset_store.asset.insurer,
            insurance_plan_name=allocations[0].asset_store.asset.plan,
            insurance_policy_number=allocations[0].asset_store.asset.policy_number,
        )


class InvestmentFactory(AssetFactory):
    class Meta:
        model = Investment

    asset_type = "Investment"

    financial_institution = factory.LazyAttribute(
        lambda x: "INSTITUTION-" + str(uuid.uuid4())[:4]
    )
    account_number = factory.LazyAttribute(lambda x: "ACCOUNT-" + str(uuid.uuid4())[:4])

    @staticmethod
    def get_params(allocations):
        return dict(
            investment_institution_name=allocations[0].asset_store.asset.financial_institution,
            investment_account_number=allocations[0].asset_store.asset.account_number,
        )


class CompanyFactory(AssetFactory):
    class Meta:
        model = Company

    asset_type = "Company"

    name = factory.LazyAttribute(lambda x: "NAME-" + str(uuid.uuid4())[:4])
    registration_number = factory.LazyAttribute(
        lambda x: "REGISTRATION-" + str(uuid.uuid4())[:4]
    )
    percentage = 30
    shares_amount = 1000000

    @staticmethod
    def get_params(allocations):
        return dict(
            company_name=allocations[0].asset_store.asset.name,
            company_registration_number=allocations[0].asset_store.asset.registration_number,
            company_percentage=allocations[0].asset_store.asset.percentage,
            company_shares_amount=allocations[0].asset_store.asset.shares_amount,
        )


class ResidualFactory(AssetFactory):
    class Meta:
        model = Residual

    asset_type = "Residual"


class AssetStoreFactory(DjangoModelFactory):
    class Meta:
        model = AssetStore

    order = factory.SubFactory(core_factories.WillOrderFactory)
    asset = factory.SubFactory(AssetFactory)


class AllocationFactory(DjangoModelFactory):
    class Meta:
        model = Allocation

    parent_allocation = None
