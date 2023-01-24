from winget.models import Package, Installer, Version

def get_package_queryset(request):
	qs = Package.objects.all()
	if request.user.is_superuser:
		return qs
	return qs.filter(tenant__user=request.user)

def get_installer_queryset(request):
	qs = Installer.objects.all()
	if request.user.is_superuser:
		return qs
	return qs.filter(version__package__tenant__user=request.user)

def get_version_queryset(request):
	qs = Version.objects.all()
	if request.user.is_superuser:
		return qs
	return qs.filter(package__tenant__user=request.user)