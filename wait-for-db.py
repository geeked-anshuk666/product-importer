import os
import sys
import time
import psycopg2
from psycopg2 import OperationalError
from urllib.parse import urlparse

def wait_for_db():
    """Wait for database to be available"""
    max_wait_time = 60  # Maximum wait time in seconds
    wait_interval = 5   # Interval between checks in seconds
    elapsed_time = 0

    database_url = os.environ.get('DATABASE_URL')

    while not database_url and elapsed_time < max_wait_time:
        print("Warning: DATABASE_URL not set, waiting...")
        time.sleep(wait_interval)
        elapsed_time += wait_interval
        database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("Error: DATABASE_URL still not set after waiting")
        print("Available environment variables:")
        for key, value in os.environ.items():
            if 'DB' in key or 'DATABASE' in key:
                print(f"  {key}: {value}")
        return False

    # Parse the DATABASE_URL
    try:
        url = urlparse(database_url)
        db_name = url.path[1:]
        db_user = url.username
        db_password = url.password
        db_host = url.hostname
        db_port = url.port
    except Exception as e:
        print(f"Error parsing DATABASE_URL: {e}")
        return False

    db_conn = None
    max_retries = 30
    retry_count = 0
    
    print(f"Waiting for database at {db_host}:{db_port}...")
    
    while retry_count < max_retries:
        try:
            db_conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            print("Database is ready!")
            db_conn.close()
            return True
        except OperationalError as e:
            retry_count += 1
            print(f"Database not ready yet (attempt {retry_count}/{max_retries}): {e}")
            time.sleep(2)
    
    print("Database connection failed after maximum retries")
    return False

if __name__ == "__main__":
    if wait_for_db():
        sys.exit(0)
    else:
        sys.exit(1)