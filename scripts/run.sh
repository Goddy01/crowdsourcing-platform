#!/bin/sh

set -e

ls -la /vol/
ls -la /vol/web 

python manage.py runserver
python manage.py collectstatic --noinput 
python manage.py migrate

uwsgi --socket :9000 --workers 4 --master --enable-threads --module crowdsourcing.wsgi