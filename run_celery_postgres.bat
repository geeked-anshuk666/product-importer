@echo off
set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/product_importer_db
set REDIS_URL=redis://localhost:6379
echo Starting Celery worker with PostgreSQL database...
celery -A product_importer.celery worker --loglevel=info --pool=solo -n worker1@%h