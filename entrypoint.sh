#!/bin/sh
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput


# Créer un superuser si il n'existe pas déjà
python manage.py shell -c "exec(\"from django.contrib.auth import get_user_model\nUser = get_user_model()\nif not User.objects.filter(username='admin').exists():\n    User.objects.create_superuser('admin','test@test.com','ChangeMe15698@')\")"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 cinema.wsgi:application

