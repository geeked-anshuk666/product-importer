#!/bin/bash

# Build and start all services
echo "Building and starting Docker containers..."
docker-compose up --build

echo "Docker containers are now running!"
echo "Access the application at http://localhost:8000"