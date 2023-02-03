from django.contrib import admin
from django.contrib.admin import StackedInline, ModelAdmin, \
    RelatedOnlyFieldListFilter
from django.forms import ModelForm
from tenants.models import Tenant
from winget.authorization import get_package_queryset, get_installer_queryset, \
    get_version_queryset
from winget.models import Package, Version, Installer


class PackageAdmin(ModelAdmin):
    list_display = ('name', 'publisher', 'identifier')
    list_display_links = list_display
    list_filter = ('publisher',)

    def get_queryset(self, request):
        return get_package_queryset(request)

    def get_exclude(self, request, obj=None):
        result = super().get_exclude(request, obj)
        if not request.user.is_superuser:
            result = list(result or []) + ['tenant']
        return result

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.tenant = Tenant.objects.get(user=request.user)
        super().save_model(request, obj, form, change)

    def get_list_display(self, request):
        result = list(super().get_list_display(request))
        if request.user.is_superuser:
            return ['tenant'] + result
        return result

    def get_list_filter(self, request):
        result = list(super().get_list_filter(request))
        if request.user.is_superuser:
            return ['tenant'] + result
        return result

class InstallerForm(ModelForm):
    class Meta:
        model = Installer
        fields = '__all__'


class InstallerInline(StackedInline):
    model = Installer
    form = InstallerForm
    readonly_fields = ('sha256',)

    def get_queryset(self, request):
        return get_installer_queryset(request)

    def get_extra(self, request, obj: Version = None, **kwargs):
        # Show one empty Installer form when the version does not yet have an
        # associated installer. Otherwise, don't add another Installer form.
        if obj and obj.installer_set.exists():
            return 0
        return 1


class VersionAdmin(ModelAdmin):
    inlines = (InstallerInline,)
    list_display = ('created', 'modified', 'package', 'version')
    list_display_links = ('created', 'modified', 'version', 'package')
    list_filter = (('package', RelatedOnlyFieldListFilter),)

    def get_queryset(self, request):
        return get_version_queryset(request)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'package' and not request.user.is_superuser:
            kwargs['queryset'] = \
                Package.objects.filter(tenant__user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_list_filter(self, request):
        # Would also like to add package__tenant to list_display and
        # list_display_links. Unfortunately, Django doesn't support it.
        result = list(super().get_list_filter(request))
        if request.user.is_superuser:
            return ['package__tenant'] + result
        return result


admin.site.register(Package, PackageAdmin)
admin.site.register(Version, VersionAdmin)
