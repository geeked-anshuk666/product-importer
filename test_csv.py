import csv

with open('test_products.csv', 'r') as f:
    reader = csv.DictReader(f)
    print('Field names:', reader.fieldnames)
    print('First row:', next(reader))