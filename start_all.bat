@echo off
REM Product Importer Startup Script
REM This script starts all required services for the application

echo Starting Product Importer Application...
echo ======================================

REM Start Redis (if not already running)
echo Checking Redis...
tasklist | findstr redis-server.exe >nul
if %errorlevel% == 1 (
    echo Starting Redis...
    cd "C:\Program Files\Redis"
    start redis-server.exe
    timeout /t 3 /nobreak >nul
) else (
    echo Redis is already running
)

REM Start Celery Worker
echo Starting Celery Worker...
cd /d "E:\Fulfil_assignment\product-importer"
start "Celery Worker" /min cmd /c ".\venv\Scripts\activate.bat && celery -A product_importer.celery worker --loglevel=info --pool=solo"

REM Wait for services to start
timeout /t 5 /nobreak >nul

REM Start Django Development Server
echo Starting Django Server...
cd /d "E:\Fulfil_assignment\product-importer"
start "Django Server" cmd /c ".\venv\Scripts\activate.bat && python manage.py runserver"

echo.
echo All services started successfully!
echo.
echo Application will be available at: http://127.0.0.1:8000
echo.
echo Press any key to exit...
pause >nul