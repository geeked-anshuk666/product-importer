# Product Importer Application - Architecture Overview

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [API Endpoints](#api-endpoints)
6. [Database Schema](#database-schema)
7. [Deployment Architecture](#deployment-architecture)

## System Architecture

The Product Importer application follows a modern web application architecture with the following key characteristics:

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Frontend      │    │   Django API     │    │   Background     │
│   (HTML/JS)     │◄──►│   (REST API)     │◄──►│   Workers        │
└─────────────────┘    └──────────────────┘    └──────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────┐         ┌──────────────┐
                       │ PostgreSQL  │         │    Redis     │
                       │  Database   │         │  (Message    │
                       └─────────────┘         │   Broker)    │
                                               └──────────────┘
```

## Technology Stack

### Backend
- **Framework**: Django 4.2.7 with Django REST Framework
- **Database**: PostgreSQL (production), SQLite (development)
- **Task Queue**: Celery with Redis as message broker
- **Web Server**: Gunicorn for production deployment
- **Static Files**: Bootstrap 5 for frontend styling

### Frontend
- **HTML Templates**: Django templating engine
- **Styling**: Bootstrap 5 CSS framework
- **JavaScript**: jQuery for AJAX interactions
- **Real-time Updates**: Polling for progress updates

### Deployment
- **Platform**: Heroku (with support for other cloud providers)
- **Process Management**: Procfile with web and worker processes
- **Dependencies**: requirements.txt for Python packages

## Core Components

### 1. Products App
Manages product entities with CRUD operations:
- Product model with SKU, name, description, and active status
- REST API endpoints for product management
- Filtering and pagination support
- Webhook notifications for product events

### 2. Uploads App
Handles large CSV file imports:
- Upload model to track file processing status
- Asynchronous processing using Celery workers
- Progress tracking with real-time updates
- Duplicate handling with case-insensitive SKU matching

### 3. Webhooks App
Manages outgoing webhook notifications:
- Webhook model with URL, event type, and status
- Event types: product_imported, product_updated, product_deleted, all_products_deleted
- Testing functionality for webhook endpoints
- Asynchronous delivery using Celery tasks

### 4. Frontend Interface
User-friendly web interface with:
- File upload with progress visualization
- Product management dashboard
- Webhook configuration panel
- Responsive design using Bootstrap

## Data Flow

### CSV Import Process

1. **File Upload**
   - User selects and uploads CSV file through web interface
   - File is stored on server and upload record created
   - Upload status set to "pending"

2. **Asynchronous Processing**
   - Celery task triggered to process the uploaded file
   - Upload status updated to "processing"
   - CSV file is parsed row by row
   - Products are created or updated based on SKU (case-insensitive)
   - Progress is updated every 100 rows

3. **Completion**
   - Upload status updated to "completed" or "failed"
   - Webhook notifications sent for import completion
   - Frontend polls for progress updates

### Product Management

1. **Create/Update**
   - User creates or updates product through web interface
   - API request sent to Django backend
   - Product saved to database
   - Webhook notification sent for product events

2. **Delete**
   - User deletes individual product or all products
   - API request sent to Django backend
   - Product(s) removed from database
   - Webhook notification sent for deletion events

### Webhook Notifications

1. **Configuration**
   - User adds/edits webhooks through web interface
   - Webhook settings stored in database
   - Event types and active status configured

2. **Delivery**
   - Events trigger webhook notifications
   - Celery task sends HTTP POST to configured URLs
   - Optional secret key for authentication
   - Delivery results logged for monitoring

## API Endpoints

### Product Endpoints
- `GET /api/products/` - List all products (with filtering)
- `POST /api/products/` - Create new product
- `GET /api/products/{id}/` - Retrieve specific product
- `PUT /api/products/{id}/` - Update specific product
- `DELETE /api/products/{id}/` - Delete specific product
- `DELETE /api/products/bulk-delete/` - Delete all products

### Upload Endpoints
- `POST /api/uploads/` - Create new upload record
- `GET /api/uploads/{id}/` - Get upload progress
- `POST /api/uploads/{id}/process/` - Process upload (deprecated, now automatic)

### Webhook Endpoints
- `GET /api/webhooks/` - List all webhooks
- `POST /api/webhooks/` - Create new webhook
- `GET /api/webhooks/{id}/` - Retrieve specific webhook
- `PUT /api/webhooks/{id}/` - Update specific webhook
- `DELETE /api/webhooks/{id}/` - Delete specific webhook
- `POST /api/webhooks/{id}/test/` - Test webhook delivery

## Database Schema

### Products Table
```sql
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_is_active ON products(is_active);
CREATE INDEX idx_products_created_at ON products(created_at);
```

### Uploads Table
```sql
CREATE TABLE uploads (
    id BIGSERIAL PRIMARY KEY,
    file VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total_rows INTEGER DEFAULT 0,
    processed_rows INTEGER DEFAULT 0,
    failed_rows INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES auth_user(id)
);

-- Indexes
CREATE INDEX idx_uploads_status ON uploads(status);
CREATE INDEX idx_uploads_created_at ON uploads(created_at);
```

### Webhooks Table
```sql
CREATE TABLE webhooks (
    id BIGSERIAL PRIMARY KEY,
    url VARCHAR(500) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    secret_key VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_webhooks_event_type ON webhooks(event_type);
CREATE INDEX idx_webhooks_is_active ON webhooks(is_active);
CREATE INDEX idx_webhooks_created_at ON webhooks(created_at);
```

## Deployment Architecture

### Heroku Deployment

The application is configured for deployment on Heroku with the following processes:

1. **Web Process**
   - Runs Django application with Gunicorn
   - Serves both API endpoints and frontend templates
   - Handles HTTP requests from users

2. **Worker Process**
   - Runs Celery worker for background tasks
   - Processes CSV file imports asynchronously
   - Sends webhook notifications
   - Connects to Redis for task queue

### Environment Variables

The application uses environment variables for configuration:

- `DATABASE_URL` - PostgreSQL database connection string
- `REDIS_URL` - Redis connection string for Celery
- `SECRET_KEY` - Django secret key for security
- `DEBUG` - Django debug mode (should be False in production)

### Scaling Considerations

1. **Horizontal Scaling**
   - Multiple web dynos can be run for high availability
   - Multiple worker dynos for processing uploads in parallel
   - Database connection pooling for handling concurrent requests

2. **Performance Optimization**
   - Database indexes on frequently queried fields
   - Asynchronous processing for long-running operations
   - Pagination for large result sets
   - Caching strategies for frequently accessed data

3. **Monitoring**
   - Progress tracking for long-running imports
   - Webhook delivery logging
   - Error handling and retry mechanisms
   - Health checks for system components

This architecture provides a robust, scalable solution for importing large CSV files while maintaining a responsive user interface and reliable webhook notifications.