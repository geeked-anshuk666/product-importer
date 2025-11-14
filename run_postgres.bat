@echo off
set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/product_importer_db
set REDIS_URL=redis://localhost:6379
echo Starting application with PostgreSQL database...
python manage.py runserver