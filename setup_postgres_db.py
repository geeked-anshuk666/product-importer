import psycopg2
import sys

conn = None
try:
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        host='localhost',
        database='postgres',
        user='postgres',
        password='postgres'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Create database
    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'product_importer_db'")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute('CREATE DATABASE product_importer_db')
        print('Database created successfully')
    else:
        print('Database already exists')
        
except psycopg2.OperationalError as e:
    print(f"Authentication failed. You may need to set a password for the postgres user.")
    print(f"Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
finally:
    if conn:
        conn.close()