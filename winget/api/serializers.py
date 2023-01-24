from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from winget.models import Package, Version, Installer


class PackageSerializer(ModelSerializer):

    class Meta:
        model = Package
        fields = ('id', 'identifier', 'name', 'publisher', 'description')

    def create(self, validated_data):
        validated_data['tenant'] = _get_tenant(self)
        return super().create(validated_data)


class UserCanAccessPackage:
    requires_context = True
    def __call__(self, value, serializer):
        if value['package'].tenant != _get_tenant(serializer):
            raise ValidationError('Unknown package.')


class VersionSerializer(ModelSerializer):

    class Meta:
        model = Version
        fields = ('id', 'package', 'version')
        validators = [UserCanAccessPackage()]


class UserCanAccessVersion:
    requires_context = True
    def __call__(self, value, serializer):
        if value['version'].package.tenant != _get_tenant(serializer):
            raise ValidationError('Unknown package.')


class InstallerSerializer(ModelSerializer):
    class Meta:
        model = Installer
        fields = \
	        ('id', 'version', 'architecture', 'type', 'scope', 'file', 'sha256')
        read_only_fields = ['sha256']
        validators = [UserCanAccessVersion()]

def _get_tenant(serializer):
    return serializer.context['request'].user.tenant_set.get()