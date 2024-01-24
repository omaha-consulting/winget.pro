from django.db.models import CharField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from functools import wraps
from os.path import splitext
from random import Random
from tenants.models import Tenant

import json
import string

def CharFieldFromChoices(*choices, **kwargs):
    return CharField(
        choices=[(c, c) for c in choices], max_length=max(map(len, choices)),
        **kwargs
    )

def parse_jsonrequest(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        data = json.loads(request.body)
        return func(request, data, *args, **kwargs)

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

def randomize_filename(filename, seed=None, prefix='-', suffix='', length=10):
    basename, extension = splitext(filename)
    letters = string.ascii_letters + string.digits
    random = Random(seed)
    random_suffix = ''.join(random.choice(letters) for _ in range(length))
    return basename + prefix + random_suffix + suffix + extension