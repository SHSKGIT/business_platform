#!/bin/bash

set -e  # Exit on error

export DJANGO_SETTINGS_MODULE=webapp.settings.prod

# Load environment variables from the .env file
set -a
source /business_platform/webapp/webapp/webapp/settings/.env
set +a

echo "Collecting static files..."
python manage.py collectstatic --noinput --verbosity 2
echo "Static files collected."

# allow to use openai>=1.0.0, automatically upgrade codebase to use the 1.0.0 interface
#openai migrate

# Wait until MySQL is ready
echo "Waiting for database connection..."

while ! nc -z db $DATABASE_PORT; do
  sleep 1 # wait for 1 second before checking again
done

echo "Database is up - executing command"

echo "Running Alembic migrations..."
alembic upgrade head
echo "Alembic migrations finished."

#python -m pip install --upgrade pip

chown -R www-data:www-data /business_platform/webapp/webapp/webapp
chmod -R 755 /business_platform/webapp/webapp/webapp

uwsgi --ini /business_platform/webapp/webapp/uwsgi.ini

uvicorn webapp.asgi:application --host $ASGI_HOST --port $ASGI_PORT
