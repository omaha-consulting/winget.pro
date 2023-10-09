from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from winget.authorization import get_package_queryset, get_version_queryset
from winget.models import Package, Version, Installer


class PackageSerializer(ModelSerializer):

    class Meta:
        model = Package
        fields = ('id', 'identifier', 'name', 'publisher', 'description')

    def create(self, validated_data):
        validated_data['tenant'] = self.context['request'].user.tenant_set.get()
        return super().create(validated_data)


class VersionSerializer(ModelSerializer):

    class Meta:
        model = Version
        fields = ('id', 'package', 'version')

    def get_extra_kwargs(self):
        result = super().get_extra_kwargs()
        result['package'] = {
            'queryset': get_package_queryset(self.context['request'])
        }
        return result


class InstallerSerializer(ModelSerializer):

    class Meta:
        model = Installer
        fields = (
            'id', 'version', 'architecture', 'type', 'scope', 'file',
            'nested_installer', 'nested_installer_type', 'sha256'
        )
        read_only_fields = ['sha256']

    def get_extra_kwargs(self):
        result = super().get_extra_kwargs()
        result['version'] = {
            'queryset': get_version_queryset(self.context['request'])
        }
        return result

    def validate(self, attrs):
        errors = Installer.validate(attrs, use_verbose_names=False)
        if errors:
            raise ValidationError(errors)
        return attrs