import json
from functools import wraps

from django.db.models import CharField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from tenants.models import Tenant


def CharFieldFromChoices(*choices):
    return CharField(
        choices=[(c, c) for c in choices], max_length=max(map(len, choices))
    )


def parse_jsonrequest(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        data = json.loads(request.body)
        return func(data, *args, **kwargs)

    return inner


def load_tenant(func):
    @wraps(func)
    def inner(request, tenant_uuid, *args, **kwargs):
        tenant = get_object_or_404(Tenant, uuid=tenant_uuid)
        return func(request, tenant, *args, **kwargs)

    return inner


def return_jsonresponse(func):
    @wraps(func)
    def inner(*args, **kwargs):
        return JsonResponse({'Data': func(*args, **kwargs)})

    return inner
