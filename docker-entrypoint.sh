#!/bin/sh
set -eo pipefail

LOG_LEVEL=${IRON_LOG_LEVEL:-INFO}

case "$1" in
    "web")         exec su-exec iron gunicorn django_project.wsgi --bind 0.0.0.0:8000;;
    "celery")      exec su-exec iron celery -A django_project worker;;
    "beat")        exec su-exec iron celery -A django_project beat;;
esac

exec "$@"
