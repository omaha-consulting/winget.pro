from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Tenant

class TenantAdmin(ModelAdmin):
    list_display = ('__str__', 'uuid')

admin.site.register(Tenant, TenantAdmin)