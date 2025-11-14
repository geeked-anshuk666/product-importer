from celery import shared_task
from .models import Upload
from products.models import Product
import csv
import os


@shared_task
def process_csv_upload(upload_id):
    """
    Process a CSV upload asynchronously
    """
    try:
        upload = Upload.objects.get(id=upload_id)
        
        # Update status to processing
        upload.status = 'processing'
        upload.save()
        
        # Process the CSV file
        file_path = upload.file.path
        
        if not os.path.exists(file_path):
            upload.status = 'failed'
            upload.save()
            return f"File not found: {file_path}"
            
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            # Detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            # Get total rows for progress tracking
            upload.total_rows = sum(1 for row in reader)
            csvfile.seek(0)
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            processed_count = 0
            failed_count = 0
            
            for row in reader:
                try:
                    # Extract product data from CSV row
                    # Adjust these field names based on your CSV structure
                    sku = row.get('sku', '').strip().lower()
                    name = row.get('name', '').strip()
                    description = row.get('description', '').strip()
                    
                    if not sku or not name:
                        failed_count += 1
                        continue
                        
                    # Create or update product (case-insensitive SKU)
                    product, created = Product.objects.update_or_create(
                        sku__iexact=sku,
                        defaults={
                            'sku': sku.upper(),  # Store as uppercase
                            'name': name,
                            'description': description,
                            'is_active': True
                        }
                    )
                    
                    processed_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    continue
                
                # Update progress every 100 rows
                if processed_count % 100 == 0:
                    upload.processed_rows = processed_count
                    upload.failed_rows = failed_count
                    upload.save()
            
            # Final update
            upload.processed_rows = processed_count
            upload.failed_rows = failed_count
            upload.status = 'completed'
            upload.save()
            
            return f"Processed {processed_count} products, {failed_count} failed"
            
    except Upload.DoesNotExist:
        return f"Upload with id {upload_id} not found"
    except Exception as e:
        # Update status to failed
        try:
            upload = Upload.objects.get(id=upload_id)
            upload.status = 'failed'
            upload.save()
        except:
            pass
        return f"Failed to process upload: {str(e)}"