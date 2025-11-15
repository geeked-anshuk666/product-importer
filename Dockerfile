# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system dependencies as root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       postgresql-client build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy app and entrypoint
COPY . /app/
COPY entrypoint-web.sh /app/entrypoint-web.sh

# Ensure entrypoint is executable
RUN chmod +x /app/entrypoint-web.sh

# Create static directory (owned by root for now)
RUN mkdir -p /app/static

# Create a non-root user and set ownership
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app

USER appuser

# Expose port and use entrypoint
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint-web.sh"]
