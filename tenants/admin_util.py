from django.contrib.admin import ModelAdmin
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS, \
    FieldDoesNotExist
from django.db.models.options import normalize_together
from django.forms import ModelForm
from tenants.models import Tenant


class TenantModelForm(ModelForm):

    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def full_clean(self):
        super().full_clean()
        if not can_pick_tenant(self.user) and self.instance:
            self.instance.tenant = Tenant.objects.get(user=self.user)
            self.validate_unique_for_tenant()

    def validate_unique_for_tenant(self):
        instance = self.instance
        meta = instance._meta
        for unique_together in normalize_together(meta.unique_together):
            if 'tenant' in unique_together:
                exclude = [
                    f.name for f in meta.fields
                    if f.name != meta.pk.name and f.name not in unique_together
                ]
                try:
                    instance.validate_unique(exclude)
                except ValidationError:
                    non_tenant_unique_together = \
                        [f for f in unique_together if f != 'tenant']
                    message = instance.unique_error_message(
                        instance.__class__, non_tenant_unique_together
                    )
                    try:
                        field, = non_tenant_unique_together
                    except ValueError:
                        field = NON_FIELD_ERRORS
                    self.add_error(field, message)


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


def can_pick_tenant(user):
    return user.is_superuser


def filter_for_user(model, user):
    tenant_accessor = get_tenant_accessor(model)
    query = {tenant_accessor + '__user': user}
    return model.objects.filter(**query)


def get_tenant_accessor(model):
    return _get_tenant_accessor(model, set())

def _get_tenant_accessor(model, visited):
    visited.add(model)
    try:
        tenant_field = model._meta.get_field('tenant')
    except FieldDoesNotExist:
        for field in model._meta.get_fields():
            related_model = field.related_model
            if related_model and related_model not in visited:
                try:
                    subquery = _get_tenant_accessor(related_model, visited)
                except ValueError:
                    pass
                else:
                    return field.name + '__' + subquery
        raise ValueError('No tenant field found')
    else:
        return tenant_field.name
