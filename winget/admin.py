from django.contrib import admin
from django.contrib.admin import RelatedOnlyFieldListFilter
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from tenants.model_admin import TenantModelAdmin, TenantStackedInline
from winget.models import Package, Version, Installer


class PackageAdmin(TenantModelAdmin):
    list_display = ('name', 'publisher', 'identifier')
    list_filter = ('publisher',)


class InstallerForm(ModelForm):
    class Meta:
        model = Installer
        fields = '__all__'


    def clean(self):
        data = super().clean()
        errors = Installer.validate(data)
        if errors:
            raise ValidationError(errors)
        return data


class InstallerInline(TenantStackedInline):
    model = Installer
    form = InstallerForm
    readonly_fields = ('sha256',)

    def get_extra(self, request, obj: Version = None, **kwargs):
        # Show one empty Installer form when the version does not yet have an
        # associated installer. Otherwise, don't add another Installer form.
        if obj and obj.installer_set.exists():
            return 0
        return 1


class VersionAdmin(TenantModelAdmin):

    inlines = (InstallerInline,)
    list_display = ('created', 'modified', 'package', 'version')
    list_display_links = ('created', 'modified', 'version', 'package')
    list_filter = (('package', RelatedOnlyFieldListFilter),)


admin.site.register(Package, PackageAdmin)
admin.site.register(Version, VersionAdmin)
