from django.contrib import admin
from django.contrib.admin import StackedInline, ModelAdmin

from .models import Package, Version, Installer

class PackageAdmin(ModelAdmin):
    list_display = ('name', 'publisher', 'identifier')
    list_display_links = list_display
    list_filter = ('publisher',)

class InstallerInline(StackedInline):
    model = Installer
    extra = 0

class VersionAdmin(ModelAdmin):
    inlines = (InstallerInline,)
    list_display = ('created', 'modified', 'package', 'version')
    list_display_links = ('created', 'modified', 'version')
    list_filter = ('package__name', 'package__publisher')

admin.site.register(Package, PackageAdmin)
admin.site.register(Version, VersionAdmin)