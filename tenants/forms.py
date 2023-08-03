from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.db.models.options import normalize_together
from django.forms import ModelForm
from tenants.access import can_pick_tenant
from tenants.models import Tenant


class TenantModelForm(ModelForm):

    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def full_clean(self):
        super().full_clean()
        if not can_pick_tenant(self.user) and self.instance:
            self.instance.tenant = Tenant.objects.get(users=self.user)
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
