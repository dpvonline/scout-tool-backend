#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python manage.py migrate
python manage.py add_users
python manage.py loaddata data/main/*.json
python manage.py loaddata data/test/*.json

gunicorn backend.wsgi:application --bind 0.0.0.0:8000
