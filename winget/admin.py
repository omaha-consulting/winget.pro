from hashlib import sha256

from django.contrib.admin import StackedInline, ModelAdmin
from django.forms import ModelForm

from core import admin
from tenants.models import Tenant
from .models import Package, Installer, LocalDependency


class PackageAdmin(ModelAdmin):
    list_display = ('name', 'publisher', 'identifier')
    list_display_links = list_display
    list_filter = ('publisher',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if _is_from_superuser(request):
            return qs
        return qs.filter(tenant__user=request.user)

    def get_exclude(self, request, obj=None):
        result = super().get_exclude(request, obj)
        if not _is_from_superuser(request):
            result = list(result or []) + ['tenant']
        return result

    def save_model(self, request, obj, form, change):
        if not _is_from_superuser(request):
            obj.tenant = Tenant.objects.get(user=request.user)
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        if _is_from_superuser(request):
            self.list_display = ['tenant'] + list(PackageAdmin.list_display)
            self.list_display_links = self.list_display
            self.list_filter = ['tenant'] + list(PackageAdmin.list_filter)
        return super().changelist_view(request, extra_context)


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


class LocalDependencyInline(StackedInline):
    model = LocalDependency
    extra = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(installer__package__tenant__user=request.user)


class InstallerAdmin(ModelAdmin):
    form = InstallerForm
    inlines = (LocalDependencyInline,)
    list_display = \
        ('package', 'version', 'architecture', 'type', 'created', 'modified')
    list_display_links = ('package', 'created', 'modified')
    list_filter = ('package', 'version')
    readonly_fields = ('sha256',)

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

    def changelist_view(self, request, extra_context=None):
        if _is_from_superuser(request):
            self.list_filter = ['package__tenant'] + \
                               list(InstallerAdmin.list_filter)
            # Would also like to add package__tenant to list_display and
            # list_display_links. Unfortunately, Django doesn't support it.
        return super().changelist_view(request, extra_context)


def _is_from_superuser(request):
    return request.user.is_superuser


admin.site.register_with_order(Package, PackageAdmin, 0)
admin.site.register_with_order(Installer, InstallerAdmin, 1)