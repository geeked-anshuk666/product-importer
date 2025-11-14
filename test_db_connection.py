#!/usr/bin/env python
import os
import dj_database_url

print("Testing database connection...")
print("Environment variables:")
for key, value in os.environ.items():
    if key.startswith('DB') or key.startswith('DATABASE'):
        print(f"  {key}: {value}")

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    print(f"DATABASE_URL found: {DATABASE_URL}")
    try:
        db_config = dj_database_url.parse(DATABASE_URL)
        print(f"Parsed database config: {db_config}")
    except Exception as e:
        print(f"Error parsing DATABASE_URL: {e}")
else:
    print("No DATABASE_URL found")