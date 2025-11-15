import os
import sys
import time
import psycopg2
from urllib.parse import urlparse

def wait_for_db():
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
        print("Error: DATABASE_URL still not set after waiting.")
        sys.exit(1)

    url = urlparse(database_url)
    db_name = url.path[1:]
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port

    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=user,
                password=password,
                host=host,
                port=port
            )
            conn.close()
            print("Database is ready!")
            return
        except psycopg2.OperationalError as e:
            print(f"Database not ready yet: {e}")
            retries -= 1
            time.sleep(5)

    print("Error: Could not connect to the database.")
    sys.exit(1)

if __name__ == "__main__":
    wait_for_db()