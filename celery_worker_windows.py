import os
import django
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_importer.settings')

# Setup Django
django.setup()

# Import the Celery app
from product_importer.celery import app

# Configure for Windows
if os.name == 'nt':
    app.conf.worker_pool = 'solo'
    app.conf.worker_concurrency = 1

if __name__ == '__main__':
    app.start()