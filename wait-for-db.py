import os
import sys
import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_db():
    """Wait for database to be available"""
    # Wait a bit for environment variables to be set
    time.sleep(2)
    
    db_host = os.environ.get('DB_HOST')
    
    if not db_host:
        print("Warning: DB_HOST not set, waiting a bit more...")
        # Wait a bit more and try again
        time.sleep(5)
        db_host = os.environ.get('DB_HOST')
        
    if not db_host:
        print("Error: DB_HOST still not set after waiting")
        print("Available environment variables:")
        for key, value in os.environ.items():
            if 'DB' in key or 'DATABASE' in key:
                print(f"  {key}: {value}")
        return False
    
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'product_importer_db')
    db_user = os.environ.get('DB_USER', 'postgres')
    db_password = os.environ.get('DB_PASSWORD', 'postgres')
    
    db_conn = None
    max_retries = 30
    retry_count = 0
    
    print(f"Waiting for database at {db_host}:{db_port}...")
    
    while retry_count < max_retries:
        try:
            db_conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password,
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