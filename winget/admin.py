from hashlib import sha256

from django.contrib import admin
from django.contrib.admin import StackedInline, ModelAdmin
from django.forms import ModelForm

from tenants.models import Tenant
from .models import Package, Version, Installer


class PackageAdmin(ModelAdmin):
    list_display = ('name', 'publisher', 'identifier')
    list_display_links = list_display
    list_filter = ('publisher',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if self._is_from_superuser(request):
            return qs
        return qs.filter(tenant__user=request.user)

    def get_exclude(self, request, obj=None):
        result = super().get_exclude(request, obj)
        if not self._is_from_superuser(request):
            result = list(result or []) + ['tenant']
        return result

    def save_model(self, request, obj, form, change):
        if not self._is_from_superuser(request):
            obj.tenant = Tenant.objects.get(user=request.user)
        super().save_model(request, obj, form, change)

    def _is_from_superuser(self, request):
        return request.user.is_superuser

class InstallerForm(ModelForm):
    class Meta:
        model = Installer
        fields = '__all__'

    def save(self, commit=True):
        m = sha256()
        for chunk in self.instance.file.chunks():
            m.update(chunk)
        self.instance.sha256 = m.digest().hex()
        return super().save(commit)


class InstallerInline(StackedInline):
    model = Installer
    form = InstallerForm
    readonly_fields = ('sha256',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(version__package__tenant__user=request.user)

    def get_extra(self, request, obj: Version = None, **kwargs):
        # Show one empty Installer form when the version does not yet have an
        # associated installer. Otherwise, don't add another Installer form.
        if obj and obj.installer_set.exists():
            return 0
        return 1


class VersionAdmin(ModelAdmin):
    inlines = (InstallerInline,)
    list_display = ('created', 'modified', 'package', 'version')
    list_display_links = ('created', 'modified', 'version')
    list_filter = ('package__name', 'package__publisher')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(package__tenant__user=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'package' and not request.user.is_superuser:
            kwargs['queryset'] = \
                Package.objects.filter(tenant__user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Package, PackageAdmin)
admin.site.register(Version, VersionAdmin)
