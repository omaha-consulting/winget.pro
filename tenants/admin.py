from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Permission
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from tenants.access import can_pick_tenant
from tenants.model_admin import TenantModelAdmin
from tenants.models import Tenant

import django.contrib.auth.admin

class TenantAdmin(ModelAdmin):
    list_display = ('__str__', 'uuid')

class TenantUserCreationForm(UserCreationForm):
    def full_clean(self):
        super().full_clean()
        if not _can_see_staff_field(self.user):
            self.instance.is_staff = True

class TenantUserAdmin(UserAdmin, TenantModelAdmin):

    list_display = ('username', 'is_active')
    list_filter = ()
    add_form = TenantUserCreationForm

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        result = [(None, {'fields': ('username', 'password')})]
        permission_fields = ['is_active']
        if _can_see_staff_field(request.user):
            permission_fields.append('is_staff')
        if request.user.is_superuser:
            permission_fields.append('is_superuser')
        permission_fields.append('user_permissions')
        result.append((('Permissions'), {'fields': permission_fields}))
        result.append(
            (('Important dates'), {'fields': ('last_login', 'date_joined')})
        )
        return result

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'user_permissions':
            # A user may only assign those permissions they have themselves:
            kwargs["queryset"] = self._get_all_permissions(request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            super().save_model(request, obj, form, change)
            if not can_pick_tenant(request.user):
                try:
                    tenant = Tenant.objects.get(users=request.user)
                except ObjectDoesNotExist:
                    pass
                else:
                    tenant.users.add(obj)

    def _get_all_permissions(self, user):
        query = Q()
        for permission_string in user.get_all_permissions():
            app_label, codename = permission_string.split('.')
            query |= Q(content_type__app_label=app_label, codename=codename)
        return Permission.objects.filter(query)

def _can_see_staff_field(user):
    return user.is_superuser

admin.site.register(Tenant, TenantAdmin)

admin.site.unregister(django.contrib.auth.models.User)
admin.site.register(User, TenantUserAdmin)