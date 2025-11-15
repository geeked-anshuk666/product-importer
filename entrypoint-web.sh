#!/usr/bin/env bash
set -euo pipefail

# Wait for DB
python wait-for-db.py

# Run migrations
python manage.py migrate --noinput

# Collect static
python manage.py collectstatic --noinput || true

# Start celery in background
celery -A product_importer.celery worker --loglevel=info --concurrency=1 &

# Start Gunicorn
exec gunicorn product_importer.wsgi:application --bind 0.0.0.0:8000
