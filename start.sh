#!/bin/sh

set -o errexit
set -o nounset

echo "Apply database migrations"
python manage.py migrate
echo "Apply test user"
python manage.py add_users
echo "Load main data"
python manage.py loaddata data/main/*.json
echo "Load test data"
#python manage.py loaddata data/test/*.json
echo "Load food inspi data"
#python manage.py loaddata data/food-init/*.json

echo "Synchronising with keycloak server"
python manage.py initialize_keycloak_groups

echo "Start server"
gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --workers=5 --threads=8
