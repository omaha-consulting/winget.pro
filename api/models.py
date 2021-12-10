from django.core.validators import MinLengthValidator, RegexValidator
from django.db.models import Model, CharField, DateTimeField, ForeignKey, \
    URLField, CASCADE

from api.util import CharFieldFromChoices


class Package(Model):
    identifier = CharField(unique=True, max_length=128)
    name = CharField(max_length=256, validators=[MinLengthValidator(2)])
    publisher = CharField(max_length=256, validators=[MinLengthValidator(2)])
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.identifier}, {self.name}'


class Version(Model):
    package = ForeignKey(Package, on_delete=CASCADE)
    version = CharField(max_length=128)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.version} for {self.package.name}'


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
