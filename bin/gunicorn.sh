#!/bin/bash

NAME="gunicorn"
DJANGODIR=/srv
SOCKFILE=/var/run/wpr/gunicorn.sock
GROUP=django
NUM_WORKERS=1
NUM_THREADS=5
DJANGO_WSGI_MODULE=wpr.wsgi

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves
# (do not use --daemon)
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --threads $NUM_THREADS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=warning \
  --log-file=-