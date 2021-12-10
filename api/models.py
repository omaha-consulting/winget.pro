from django.core.validators import MinLengthValidator, RegexValidator
from django.db.models import Model, CharField, DateTimeField, ForeignKey, \
    URLField, CASCADE, TextField

from api.util import CharFieldFromChoices


class Package(Model):
    identifier = CharField(
        unique=True, max_length=128,
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

    def __str__(self):
        return self.name


class Version(Model):

    class Meta:
        unique_together = ('package', 'version')

    package = ForeignKey(Package, on_delete=CASCADE)
    version = CharField(
        max_length=128, blank=True,
        help_text="The package's version (eg. 1.2.3.4)."
    )
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.version} for {self.package.name}'


class Installer(Model):

    class Meta:
        unique_together = ('version', 'architecture', 'type')

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

    def __str__(self):
        return self.url.rsplit('/', 1)[-1]