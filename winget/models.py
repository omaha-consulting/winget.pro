from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinLengthValidator, RegexValidator
from django.db.models import Model, CharField, DateTimeField, ForeignKey, \
    CASCADE, TextField, FileField, CheckConstraint, Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from hashlib import sha256
from tenants.models import Tenant
from winget.util import CharFieldFromChoices, randomize_filename


class Package(Model):
    tenant = ForeignKey(Tenant, on_delete=CASCADE)
    identifier = CharField(
        max_length=128,
        help_text='Unique identifier for the package (e.g. WinMerge.WinMerge).'
    )
    name = CharField(
        max_length=256, validators=[MinLengthValidator(2)],
        help_text='Package name (e.g. WinMerge).'
    )
    publisher = CharField(
        max_length=256, validators=[MinLengthValidator(2)],
        help_text='Package publisher (eg. Thingamahoochie Software)'
    )
    description = TextField(
        max_length=256, validators=[MinLengthValidator(3)],
        help_text=
            'Package description (e.g. "An open source differencing tool.")'
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
        help_text="The package's version (eg. 2.16.26 or 1.2.3.4)."
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


def installer_upload_to(instance, filename):
    # Randomize the upload path. This prevents users from guessing it and
    # prevents clashes.
    randomized_filename = randomize_filename(filename)
    return f'{instance.version.package.tenant.uuid}/{randomized_filename}'


class Installer(Model):
    version = ForeignKey(Version, on_delete=CASCADE)
    architecture = CharFieldFromChoices('x86', 'x64', 'arm', 'arm64')
    scope = CharFieldFromChoices(
        'user', 'machine', 'both', default='both',
        help_text=
        "Is this a machine-wide installer, just for the current user, or both?"
    )
    type = CharFieldFromChoices(
        'msix', 'msi', 'appx', 'exe', 'zip', 'inno', 'nullsoft', 'wix', 'burn',
        'pwa', 'msstore'
    )
    file = FileField(upload_to=installer_upload_to)
    nested_installer = CharField(
        blank=True, max_length=512, help_text=
        "If this is a zip file, which installer inside it should be run?"
    )
    nested_installer_type = CharFieldFromChoices(
        'msix', 'msi', 'appx', 'exe', 'inno', 'nullsoft', 'wix', 'burn',
        'portable', blank=True, null=True, help_text=
        "If this is a zip file, what's the type of the nested installer?"
    )
    silent_switch = CharField(
        blank=True, max_length=512, help_text=
        "Setting this to abc makes `winget install --silent` run "
        "`installer.exe abc`."
    )
    silent_progress_switch = CharField(
        blank=True, max_length=512, help_text=
        "Setting this to abc makes `winget install` (without modifiers) run "
        "`installer.exe abc`."
    )
    interactive_switch = CharField(
        blank=True, max_length=512, help_text=
        "Setting this to abc makes `winget install --interactive` run "
        "`installer.exe abc`."
    )
    install_location_switch = CharField(
        blank=True, max_length=512, help_text=
        'Setting this to "abc &lt;INSTALLPATH&gt;" makes `winget install '
        '--location C:\Dir` run `installer.exe abc C:\Dir`.'
    )
    log_switch = CharField(blank=True, max_length=512, help_text=
        'Setting this to "abc &lt;LOGPATH&gt;" runs `installer.exe abc '
        '&lt;some file path&gt;`. Set the path with `winget install --log`.'
    )
    upgrade_switch = CharField(
        blank=True, max_length=512, help_text=
        "The installer's command-line argument when the user chooses an upgrade."
    )
    custom_switch = CharField(
        blank=True, max_length=512, help_text=
        "Setting this to abc always appends `abc` to the installer's "
        "command-line. Eg. `installer.exe abc`."
    )
    sha256 = CharField(
        max_length=64, validators=[RegexValidator('^[a-fA-F0-9]{64}$')]
    )
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('version', 'architecture', 'type')
        # N.B.: The constraints here need to be checked in .validate(...) too.
        constraints = [
            CheckConstraint(
                check=(Q(type='zip') & ~Q(nested_installer='')) | \
                      (~Q(type='zip') & Q(nested_installer='')),
                name='nested_installer_iff_zip'
            ),
            CheckConstraint(
                check=(Q(type='zip') & ~Q(nested_installer_type=None)) | \
                      (~Q(type='zip') & Q(nested_installer_type=None)),
                name='nested_installer_type_iff_zip'
            ),
        ]

    @classmethod
    def validate(cls, data):
        # If possible, the checks here should be in Meta.constraints too.
        errors = {}
        def add_error(field, message):
            field_name = cls._meta.get_field(field).verbose_name.capitalize()
            errors[field] = field_name + ' ' + message
        if data.get('type') == 'zip':
            if not data.get('nested_installer'):
                add_error('nested_installer', 'is required when type is "zip".')
            if not data.get('nested_installer_type'):
                add_error(
                    'nested_installer_type', 'is required when type is "zip".'
                )
        else:
            if data.get('nested_installer'):
                add_error(
                    'nested_installer', 'can only be set when type is "zip".'
                )
            if data.get('nested_installer_type'):
                add_error(
                    'nested_installer_type',
                    'can only be set when type is "zip".'
                )
        return errors

    @property
    def scopes(self):
        return ['user', 'machine'] if self.scope == 'both' else [self.scope]

    def __str__(self):
        result_parts = []
        try:
            result_parts.append(str(self.version))
        except ObjectDoesNotExist:
            pass
        if self.architecture:
            result_parts.append(self.architecture)
        if self.scope != 'both':
            result_parts.append(self.scope)
        return ' '.join(result_parts)


@receiver(pre_save, sender=Installer)
def pre_installer_save(sender, instance, **kwargs):
    m = sha256()
    instance.file.seek(0)
    for chunk in instance.file.chunks():
        m.update(chunk)
    instance.sha256 = m.digest().hex()