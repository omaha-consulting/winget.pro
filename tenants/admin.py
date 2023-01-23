from django.contrib.admin import ModelAdmin

from core import admin
from .models import Tenant

class TenantAdmin(ModelAdmin):
    list_display = ('user', 'uuid')

admin.site.register(Tenant, TenantAdmin)