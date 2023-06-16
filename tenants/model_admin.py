from django.contrib.admin import ModelAdmin
from tenants.access import can_pick_tenant, filter_for_user, get_tenant_accessor
from tenants.forms import TenantModelForm


class TenantModelAdmin(ModelAdmin):

    form = TenantModelForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if can_pick_tenant(request.user):
            return qs
        return qs & filter_for_user(self.model, request.user)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.user = request.user
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not can_pick_tenant(request.user):
            tenant_model = db_field.related_model
            kwargs['queryset'] = filter_for_user(tenant_model, request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_exclude(self, request, obj=None):
        result = super().get_exclude(request, obj)
        if not can_pick_tenant(request.user):
            result = list(result or []) + ['tenant']
        return result

    def get_list_display(self, request):
        result = list(super().get_list_display(request))
        if can_pick_tenant(request.user):
            tenant_accessor = get_tenant_accessor(self.model)
            # Django doesn't support transitive relations in list_display:
            if '__' not in tenant_accessor:
                result = [tenant_accessor] + result
        return result

    def get_list_display_links(self, request, list_display):
        return self.get_list_display(request)

    def get_list_filter(self, request):
        result = list(super().get_list_filter(request))
        if can_pick_tenant(request.user):
            result = [get_tenant_accessor(self.model)] + result
        return result

    def lookup_allowed(self, lookup, value):
        # Allow filtering by tenant for models whose tenant field is transitive.
        # For example: Version -> Package -> Tenant. As a superuser, we want to
        # be able to filter versions by tenant. Without the following code, we
        # would get a `DisallowedModelAdminLookup` when trying to do this.
        tenant_accessor = get_tenant_accessor(self.model)
        if lookup == tenant_accessor + '__id__exact':
            return True
        return super().lookup_allowed(lookup, value)
