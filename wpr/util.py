import os

from django.core.exceptions import ImproperlyConfigured


def get_bool_from_env(name, default):
    result_str = os.getenv(name)
    if not result_str:
        return default
    if result_str == 'True':
        return True
    elif result_str == 'False':
        return False
    raise ImproperlyConfigured(
        'Environment variable %r has invalid value. Must be True or False.'
        % name
    )
