#!/bin/bash

cd /srv
git pull
venv/bin/pip install -U pip | grep -v "^Requirement already satisfied"
venv/bin/pip install -Ur requirements/base-full.txt | grep -v "^Requirement already satisfied"
su -c '/srv/run/vps/bin/manage.sh migrate | grep -v "INFO\|DEBUG"' - django
su -c '/srv/run/vps/bin/manage.sh collectstatic --noinput | grep -v "INFO\|DEBUG"' - django

echo `date +%H:%M:%S`': Reloading web server...'

# Reload gunicorn:
supervisorctl status gunicorn | sed "s/.*[pid ]\([0-9]\+\)\,.*/\1/" | xargs kill -HUP

# Reload Nginx:
nginx -s reload

echo `date +%H:%M:%S`': Web server reload complete.'

# Update crontab:
sed "s/\$ADMIN_EMAIL/$ADMIN_EMAIL/g" /srv/run/vps/conf/crontab | crontab -