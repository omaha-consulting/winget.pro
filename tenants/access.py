from django.core.exceptions import FieldDoesNotExist


def can_pick_tenant(user):
    return user.is_superuser


def filter_for_user(model, user):
    tenant_accessor = get_tenant_accessor(model)
    query = {tenant_accessor + '__user': user}
    return model.objects.filter(**query)


def get_tenant_accessor(model):
    return _get_tenant_accessor(model, set())


def _get_tenant_accessor(model, visited):
    visited.add(model)
    try:
        tenant_field = model._meta.get_field('tenant')
    except FieldDoesNotExist:
        for field in model._meta.get_fields():
            related_model = field.related_model
            if related_model and related_model not in visited:
                try:
                    subquery = _get_tenant_accessor(related_model, visited)
                except ValueError:
                    pass
                else:
                    return field.name + '__' + subquery
        raise ValueError('No tenant field found')
    else:
        return tenant_field.name
