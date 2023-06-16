from tenants.admin_util import filter_for_user
from winget.models import Package, Installer, Version

def get_package_queryset(request):
	return filter_for_user(Package, request.user)

def get_installer_queryset(request):
	return filter_for_user(Installer, request.user)

def get_version_queryset(request):
	return filter_for_user(Version, request.user)