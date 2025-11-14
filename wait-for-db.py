import os
import sys
import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_db():
    """Wait for database to be available"""
    db_host = os.environ.get('DB_HOST')
    
    if not db_host:
        print("Warning: DB_HOST not set, skipping database wait")
        return
    
    db_conn = None
    max_retries = 30
    retry_count = 0
    
    print(f"Waiting for database at {db_host}...")
    
    while retry_count < max_retries:
        try:
            db_conn = psycopg2.connect(
                host=os.environ.get('DB_HOST'),
                port=os.environ.get('DB_PORT', '5432'),
                database=os.environ.get('DB_NAME', 'product_importer_db'),
                user=os.environ.get('DB_USER', 'postgres'),
                password=os.environ.get('DB_PASSWORD', 'postgres'),
            )
            print("Database is ready!")
            db_conn.close()
            return
        except OperationalError as e:
            retry_count += 1
            print(f"Database not ready yet (attempt {retry_count}/{max_retries}): {e}")
            time.sleep(2)
    
    print("Database connection failed after maximum retries")
    sys.exit(1)

if __name__ == "__main__":
    wait_for_db()