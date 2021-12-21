from django.apps import AppConfig


class TenantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tenants'

    def ready(self):
        super().ready()
        _ensure_tenants_group_exists()


def _ensure_tenants_group_exists():
    """
    Make sure the "Tenants" group exists so users can be assigned to it.
    Normally, we would want to do this in a migration. Unfortunately, Django
    cannot currently (easily) assign permissions in a migration [1].
    The `ready()` method above seems like a reasonable place to do it instead.
    """
    # We cannot import the following at the module level because Django has not
    # been initialized yet:
    from django.contrib.auth.models import Group, Permission
    from winget.models import Package, Version, Installer
    group, created = Group.objects.get_or_create(name='Tenants')
    if created:
        for model in (Package, Version, Installer):
            for action in ('view', 'add', 'change', 'delete'):
                codename = f'{action}_{model._meta.model_name}'
                permission = Permission.objects.get(codename=codename)
                group.permissions.add(permission)
