from celery import shared_task
from .models import Upload
from products.models import Product
import csv
import os
import logging
from django.db import transaction
from collections import defaultdict

# Set up logging
logger = logging.getLogger(__name__)


def estimate_csv_rows(file_path, sample_size=1024):
    """
    Efficiently estimate the number of rows in a CSV file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read a sample of the file
            sample = f.read(sample_size)
            # Count newlines in sample
            newline_count = sample.count('\n')
            # Get file size
            file_size = os.path.getsize(file_path)
            # Estimate total rows
            estimated_rows = int((file_size / sample_size) * newline_count)
            return max(1, estimated_rows)  # Ensure at least 1
    except:
        return 1000  # Default estimate


def extract_product_data(row):
    """
    Extract product data from a CSV row, handling different possible formats
    """
    # Default values
    sku = None
    name = None
    description = ""
    
    # Common field name variations for SKU
    sku_fields = ['uniq_id', 'sku', 'product_sku', 'product-id', 'product_id', 'id', 'item_sku', 'pid']
    # Common field name variations for name
    name_fields = ['product_name', 'name', 'title', 'product-title', 'item_name']
    # Common field name variations for description
    desc_fields = ['description', 'desc', 'product_description', 'item_description']
    
    # Try to find fields by name (case insensitive)
    for key, value in row.items():
        key_lower = key.lower().strip()
        value_stripped = value.strip() if value else ""
        
        if key_lower in sku_fields:
            sku = value_stripped.lower() if value_stripped else None
        elif key_lower in name_fields:
            name = value_stripped if value_stripped else None
        elif key_lower in desc_fields:
            description = value_stripped
    
    # If we couldn't find fields by name, try positional approach
    if sku is None or name is None:
        values = [v.strip() if v else "" for v in row.values()]
        if len(values) >= 2:
            # For this specific file format, the first column is uniq_id and second is product_name
            if sku is None and values[0]:
                sku = values[0].lower()
            if name is None and values[3]:  # product_name is the 4th column (index 3)
                name = values[3]
            if len(values) > 5 and not description:  # description might be in later columns
                description = values[5]
    
    return sku, name, description


@shared_task
def process_csv_upload(upload_id):
    """
    Process a CSV upload asynchronously with optimizations for large files
    """
    try:
        upload = Upload.objects.get(id=upload_id)
        
        # Update status to processing immediately with initial values
        upload.status = 'processing'
        upload.total_rows = 1000  # Initial estimate to avoid 0% progress
        upload.processed_rows = 0
        upload.failed_rows = 0
        upload.save()
        
        # Process the CSV file
        file_path = upload.file.path
        
        if not os.path.exists(file_path):
            upload.status = 'failed'
            upload.save()
            return f"File not found: {file_path}"
        
        # Estimate total rows for progress tracking
        estimated_total_rows = estimate_csv_rows(file_path)
        upload.total_rows = estimated_total_rows
        upload.save()
        
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            # Detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            # Log the field names to help with debugging
            fieldnames = reader.fieldnames
            logger.info(f"CSV field names: {fieldnames}")
            print(f"CSV field names: {fieldnames}")
            
            processed_count = 0
            failed_count = 0
            error_details = []
            
            # Batch processing variables
            batch_size = 1000  # Process 1000 products at a time
            product_batch = []
            batch_counter = 0
            
            for i, row in enumerate(reader):
                try:
                    # Extract product data from CSV row
                    sku, name, description = extract_product_data(row)
                    
                    # Validate required fields
                    if not sku:
                        failed_count += 1
                        if len(error_details) < 10:  # Only log first 10 errors
                            error_details.append(f"Row {i+1}: Missing SKU. Row data: {row}")
                        continue
                        
                    if not name:
                        failed_count += 1
                        if len(error_details) < 10:  # Only log first 10 errors
                            error_details.append(f"Row {i+1}: Missing name. Row data: {row}")
                        continue
                        
                    # Add to batch
                    product_batch.append({
                        'sku': sku.upper(),  # Store as uppercase
                        'name': name,
                        'description': description,
                        'is_active': True
                    })
                    
                    # When batch is full, process it
                    if len(product_batch) >= batch_size:
                        processed_in_batch = process_product_batch(product_batch, upload.id)
                        processed_count += processed_in_batch
                        product_batch = []  # Reset batch
                        
                        # Update progress
                        upload.refresh_from_db()  # Get latest data from DB
                        upload.processed_rows = processed_count
                        upload.failed_rows = failed_count
                        upload.save()
                        
                        batch_counter += 1
                        # Log progress every 10 batches
                        if batch_counter % 10 == 0:
                            logger.info(f"Processed {batch_counter} batches, {processed_count} products so far")
                    
                except Exception as e:
                    failed_count += 1
                    if len(error_details) < 10:  # Only log first 10 errors
                        error_details.append(f"Row {i+1}: Exception - {str(e)}. Row data: {row}")
                    continue
                
            # Process remaining products in the final batch
            if product_batch:
                processed_in_batch = process_product_batch(product_batch, upload.id)
                processed_count += processed_in_batch
                
            # Log error details if there were failures
            if error_details:
                error_summary = f"First {len(error_details)} errors:\n" + "\n".join(error_details)
                logger.error(error_summary)
                print(error_summary)
            
            # Final update with actual counts
            upload.refresh_from_db()  # Get latest data from DB
            upload.processed_rows = processed_count
            upload.failed_rows = failed_count
            upload.total_rows = processed_count + failed_count
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


def process_product_batch(product_batch, upload_id):
    """
    Process a batch of products using bulk operations for better performance
    """
    try:
        # Use a more efficient approach: bulk create with conflict resolution
        # First, get all SKUs in this batch
        skus_in_batch = [product['sku'] for product in product_batch]
        
        # Find existing products with these SKUs (case-insensitive)
        existing_products = Product.objects.filter(sku__in=skus_in_batch)
        existing_sku_dict = {product.sku: product for product in existing_products}
        
        # Separate products to create and update
        products_to_create = []
        products_to_update = []
        
        for product_data in product_batch:
            sku = product_data['sku']
            if sku in existing_sku_dict:
                # Update existing product
                existing_product = existing_sku_dict[sku]
                existing_product.name = product_data['name']
                existing_product.description = product_data['description']
                existing_product.is_active = product_data['is_active']
                products_to_update.append(existing_product)
            else:
                # Create new product
                products_to_create.append(Product(**product_data))
        
        # Bulk operations
        if products_to_create:
            Product.objects.bulk_create(products_to_create, ignore_conflicts=True)
        
        if products_to_update:
            Product.objects.bulk_update(products_to_update, ['name', 'description', 'is_active'])
        
        return len(product_batch)
        
    except Exception as e:
        logger.error(f"Error processing batch for upload {upload_id}: {str(e)}")
        # If bulk operations fail, fall back to individual processing
        processed_count = 0
        for product_data in product_batch:
            try:
                Product.objects.update_or_create(
                    sku__iexact=product_data['sku'],
                    defaults=product_data
                )
                processed_count += 1
            except Exception as inner_e:
                logger.error(f"Error processing individual product: {str(inner_e)}")
        return processed_count