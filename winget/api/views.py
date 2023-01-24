from rest_framework.viewsets import ModelViewSet
from winget.api.serializers import PackageSerializer, VersionSerializer, \
	InstallerSerializer
from winget.authorization import get_package_queryset, get_version_queryset, \
	get_installer_queryset

class PackageViewSet(ModelViewSet):
    serializer_class = PackageSerializer
    def get_queryset(self):
        return get_package_queryset(self.request)

class VersionViewSet(ModelViewSet):
    serializer_class = VersionSerializer
    def get_queryset(self):
        return get_version_queryset(self.request)

class InstallerViewSet(ModelViewSet):
    serializer_class = InstallerSerializer
    def get_queryset(self):
        return get_installer_queryset(self.request)