#!/usr/bin/env bash
# start-server.sh

(python page_microservice/manage.py collectstatic --noinput; cd page_microservice; gunicorn page_microservice.wsgi --user www-data --bind 0.0.0.0:8040 --workers 3 --error-logfile /opt/page_ms_assets/logs/gunicorn/error.log --access-logfile /opt/page_ms_assets/logs/gunicorn/access.log --log-level=INFO;)
