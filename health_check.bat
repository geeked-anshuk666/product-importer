@echo off
REM Product Importer Health Check Script
REM This script checks if all required services are running

echo Product Importer Health Check
echo =============================

REM Check Redis
echo Checking Redis...
tasklist | findstr redis-server.exe >nul
if %errorlevel% == 0 (
    echo [OK] Redis is running
) else (
    echo [ERROR] Redis is not running
    echo Please start Redis server
)

REM Check Celery Worker
echo Checking Celery Worker...
tasklist | findstr celery.exe >nul
if %errorlevel% == 0 (
    echo [OK] Celery Worker is running
) else (
    echo [WARNING] Celery Worker is not running
    echo Please start Celery worker with: celery -A product_importer.celery worker --loglevel=info --pool=solo
)

REM Check Django Server
echo Checking Django Server...
tasklist | findstr "python.*manage.py" >nul
if %errorlevel% == 0 (
    echo [OK] Django Server is running
) else (
    echo [WARNING] Django Server is not running
    echo Please start Django server with: python manage.py runserver
)

echo.
echo Health check completed.
pause