from django.contrib import admin

from .models import *

# Register your models here.


class PersonalDetailsAdminManager(admin.ModelAdmin):

    search_fields = ["user__email", "willcraftuser__email"]
    list_display = ["name", "id_number"]


admin.site.register(Person, PersonalDetailsAdminManager)


class PersonAdminManager(admin.ModelAdmin):

    search_fields = ["order__user__email", "order__order_number"]

    list_display = ["__str__", "get_entity_roles"]

    def get_entity_roles(self, obj):
        return "\n".join([p.type_name for p in obj.entity_roles.all()])


admin.site.register(EntityStore, PersonAdminManager)
admin.site.register(DoneePowers)
admin.site.register(Entity)
