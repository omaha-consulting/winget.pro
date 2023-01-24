from rest_framework.routers import DefaultRouter
from winget.api.views import PackageViewSet, VersionViewSet, InstallerViewSet

router = DefaultRouter()

router.register('packages', PackageViewSet, 'package')
router.register('versions', VersionViewSet, 'version')
router.register('installers', InstallerViewSet, 'installer')