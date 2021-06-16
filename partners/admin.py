from django.contrib import admin
from django.db.models import Count

from billing.models import Discount

from .models import *

# Register your models here.


class ApplicationStoreAdmin(admin.TabularInline):
    model = ApplicationStore
    extra = 1


class PartnersAdmin(admin.ModelAdmin):
    inlines = [ApplicationStoreAdmin]
    list_display = (
        "name",
        "number_of_referred_users",
        "get_referred_users",
        "get_applications",
        "get_agents",
        "get_managers",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'agents',
            'managers',
            'application_stores',
            'application_stores__application',
            'application_stores__referred_users',
        ).annotate(
            users_count=Count('application_stores__referred_users', distinct=True)
        )

    def get_applications(self, obj):
        applications = obj.application_stores.select_related('application').all()
        if applications:
            return "\n".join([p.application.name for p in applications])
        return None

    def get_agents(self, obj):
        agents = obj.agents.all()
        if agents:
            return "\n".join([p.email for p in agents])
        return None

    def get_managers(self, obj):
        managers = obj.managers.all()
        if managers:
            return "\n".join([p.email for p in managers])
        return None

    def get_referred_users(self, obj):
        application_stores = obj.application_stores.select_related('application').all()
        if application_stores:
            for application_store in application_stores:
                referred_users = application_store.referred_users.all()
                if referred_users:
                    return ", ".join([p.email for p in referred_users])
        return None

    def number_of_referred_users(self, obj):
        return obj.users_count


admin.site.register(Partners, PartnersAdmin)
