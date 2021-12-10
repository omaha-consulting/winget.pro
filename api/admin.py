from django.contrib import admin

from .models import Package, Version, Installer

admin.site.register(Package)
admin.site.register(Version)
admin.site.register(Installer)