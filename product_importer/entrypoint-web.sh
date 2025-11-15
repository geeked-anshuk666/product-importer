#!/usr/bin/env bash
set -euo pipefail

# Wait for DB (your present script)
python wait-for-db.py

# Run migrations (idempotent)
python manage.py migrate --noinput

# Collect static (don't fail if something is missing)
python manage.py collectstatic --noinput || true

# Start celery in background (hobby mode, low resource)
celery -A product_importer.celery worker --loglevel=info --concurrency=1 &

# Exec gunicorn so it receives signals properly
exec gunicorn product_importer.wsgi:application --bind 0.0.0.0:8000
