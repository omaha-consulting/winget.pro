import json

from functools import wraps

from django.db.models import CharField
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST


def CharFieldFromChoices(*choices):
    return CharField(
        choices=[(c, c) for c in choices], max_length=max(map(len, choices))
    )


def json_get(func):
    @require_GET
    @json_response
    def inner(_, *args, **kwargs):
        return func(*args, **kwargs)

    return inner


def json_post(func):
    return csrf_exempt(require_POST(json_request(json_response(func))))


def json_response(func):
    @wraps(func)
    def inner(*args, **kwargs):
        return JsonResponse({'Data': func(*args, **kwargs)})

    return inner


def json_request(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        data = json.loads(request.body)
        return func(data, *args, **kwargs)

    return inner
