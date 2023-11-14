#!/bin/sh

echo $SHELL

set -e

python manage.py migrate

if [ -n "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser --noinput
fi

gunicorn core.wsgi:application --bind 0.0.0.0:8000 --log-level=warning \
    --log-file=-