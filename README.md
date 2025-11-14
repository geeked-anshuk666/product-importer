# Product Importer Application

A web application for importing large CSV files of products into a database with a focus on scalability and performance.

## Features

- Upload large CSV files (up to 500,000 products) through a web interface
- Real-time progress indication during file processing
- Product management (CRUD operations) through web interface
- Webhook configuration for event notifications
- Bulk delete functionality with confirmation
- Responsive web interface built with Bootstrap

## Technology Stack

- **Backend**: Django 4.2.7 with Django REST Framework
- **Database**: PostgreSQL (production), SQLite (development)
- **Task Queue**: Celery with Redis
- **Frontend**: HTML, Bootstrap 5, jQuery
- **Deployment**: Render-ready with render.yaml

## Prerequisites

- Python 3.9+
- PostgreSQL (for production)
- Redis (for Celery)
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd product-importer
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   
   For development (SQLite):
   ```bash
   python manage.py migrate
   ```
   
   For production (PostgreSQL):
   - Create a PostgreSQL database
   - Set the DATABASE_URL environment variable
   - Run migrations

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

## Configuration

The application can be configured using environment variables:

- `DATABASE_URL`: PostgreSQL database connection string (optional, defaults to SQLite)
- `REDIS_URL`: Redis connection string for Celery (default: redis://localhost:6379)
- `SECRET_KEY`: Django secret key (required for production)
- `DEBUG`: Django debug mode (default: True for development)

## Running the Application

1. **Start the Django development server**
   ```bash
   python manage.py runserver
   ```

2. **Start the Celery worker** (in a separate terminal)
   ```bash
   celery -A product_importer.celery worker --loglevel=info
   ```

3. **Start Redis** (if not already running)
   ```bash
   redis-server
   ```

4. **Access the application**
   Open your browser and navigate to `http://localhost:8000`

## Deployment

### Render Deployment

The application is configured for deployment on Render:

1. Fork this repository to your GitHub account
2. Create a new Web Service on Render
3. Connect it to your forked repository
4. Render will automatically detect the render.yaml file and configure:
   - A web service for the Django application
   - A worker service for Celery tasks
   - A PostgreSQL database
   - A Redis instance
5. **Important**: After deployment, if you encounter "DisallowedHost" errors, add your Render domain to the ALLOWED_HOSTS in `product_importer/settings.py`
6. Click "Create" and Render will deploy the application

### Manual Deployment

1. Create a new Web Service on Render
2. Set the build command: `pip install -r requirements.txt`
3. Set the start command: `gunicorn product_importer.wsgi:application`
4. Add environment variables as needed
5. Create a separate Background Worker service with:
   - Build command: `pip install -r requirements.txt`
   - Start command: `celery -A product_importer.celery worker --loglevel=info`

## API Endpoints

### Products
- `GET /api/products/` - List all products
- `POST /api/products/` - Create a new product
- `GET /api/products/{id}/` - Retrieve a specific product
- `PUT /api/products/{id}/` - Update a specific product
- `DELETE /api/products/{id}/` - Delete a specific product
- `DELETE /api/products/bulk-delete/` - Delete all products

### Uploads
- `POST /api/uploads/` - Upload a CSV file
- `GET /api/uploads/{id}/` - Get upload progress

### Webhooks
- `GET /api/webhooks/` - List all webhooks
- `POST /api/webhooks/` - Create a new webhook
- `GET /api/webhooks/{id}/` - Retrieve a specific webhook
- `PUT /api/webhooks/{id}/` - Update a specific webhook
- `DELETE /api/webhooks/{id}/` - Delete a specific webhook
- `POST /api/webhooks/{id}/test/` - Test a webhook

## CSV File Format

The application expects CSV files with the following columns:
- `sku` (required): Product SKU (unique identifier)
- `name` (required): Product name
- `description` (optional): Product description

Example:
```csv
sku,name,description
PROD-001,Product 1,This is the first product
PROD-002,Product 2,This is the second product
```

## Architecture

For detailed information about the system architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.