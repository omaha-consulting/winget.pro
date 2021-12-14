#!/bin/bash

# We place files in /var/run/omaha. But it gets deleted on every reboot.
# This script re-creates it.

mkdir -p /var/run/wpr
chown root:django /var/run/wpr
# It's important that "others" have executable rights; Otherwise, Nginx can't
# access the Gunicorn .sock files in that directory.
chmod 731 /var/run/wpr