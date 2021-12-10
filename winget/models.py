from django.core.validators import MinLengthValidator, RegexValidator
from django.db.models import Model, CharField, DateTimeField, ForeignKey, \
    URLField, CASCADE, TextField

from tenants.models import Tenant
from winget.util import CharFieldFromChoices


class Package(Model):
    tenant = ForeignKey(Tenant, on_delete=CASCADE)
    identifier = CharField(
        max_length=128,
        help_text='Unique identifier for the package (e.g. XP9KHM4BK9FZ7Q).'
    )
    name = CharField(
        max_length=256, validators=[MinLengthValidator(2)],
        help_text='Package name (e.g. Visual Studio Code).'
    )
    publisher = CharField(
        max_length=256, validators=[MinLengthValidator(2)],
        help_text='Package publisher (eg. Microsoft Corporation)'
    )
    description = TextField(
        max_length=256, validators=[MinLengthValidator(3)],
        help_text='Package description (e.g. "Free code editor.")'
    )
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('tenant', 'identifier')

    def __str__(self):
        return self.name


class Version(Model):
    package = ForeignKey(Package, on_delete=CASCADE)
    version = CharField(
        max_length=128, blank=True,
        help_text="The package's version (eg. 1.2.3.4)."
    )
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('package', 'version')

    def __str__(self):
        result = self.package.name
        if self.version:
            result += ' ' + self.version
        return result


class Installer(Model):
    version = ForeignKey(Version, on_delete=CASCADE)
    architecture = CharFieldFromChoices('x86', 'x64', 'arm', 'arm64')
    type = CharFieldFromChoices(
        'msix', 'msi', 'appx', 'exe', 'zip', 'inno', 'nullsoft', 'wix', 'burn',
        'pwa', 'msstore'
    )
    url = URLField()
    sha256 = CharField(
        max_length=64, validators=[RegexValidator('^[a-fA-F0-9]{64}$')]
    )
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('version', 'architecture', 'type')

    def __str__(self):
        return self.url.rsplit('/', 1)[-1]
