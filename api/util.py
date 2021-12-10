import json

from functools import wraps

from django.db.models import CharField
from django.http import JsonResponse


def CharFieldFromChoices(*choices):
    return CharField(
        choices=[(c, c) for c in choices], max_length=max(map(len, choices))
    )


def json_response(func):
    @wraps(func)
    def inner(*args, **kwargs):
        return JsonResponse({'Data': func(*args, **kwargs)})

    return inner


def json_request(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        request_dict = json.loads(request.body)
        return func(request_dict, *args, **kwargs)

    return inner
