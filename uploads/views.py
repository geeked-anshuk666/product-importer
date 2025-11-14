from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Upload
from .serializers import UploadSerializer
import csv
import os
from django.conf import settings
from products.models import Product


class UploadCreateView(generics.CreateAPIView):
    queryset = Upload.objects.all()
    serializer_class = UploadSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def perform_create(self, serializer):
        # Save the upload record
        upload = serializer.save()
        
        # Process the CSV file asynchronously
        # For now, we'll just update the status to processing
        upload.status = 'processing'
        upload.save()
        
        # In a real implementation, this would trigger a Celery task
        # to process the file asynchronously
        
        

class UploadProgressView(generics.RetrieveAPIView):
    queryset = Upload.objects.all()
    serializer_class = UploadSerializer
    
    

class ProcessUploadView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        upload_id = kwargs.get('pk')
        try:
            upload = Upload.objects.get(id=upload_id)
            
            if upload.status != 'pending' and upload.status != 'processing':
                return Response({
                    'error': 'Upload is not in a valid state for processing'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # Process the CSV file
            file_path = upload.file.path
            
            if not os.path.exists(file_path):
                return Response({
                    'error': 'File not found'
                }, status=status.HTTP_404_NOT_FOUND)
                
            try:
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
                    
                    return Response({
                        'message': 'Upload processed successfully',
                        'processed': processed_count,
                        'failed': failed_count
                    }, status=status.HTTP_200_OK)
                    
            except Exception as e:
                upload.status = 'failed'
                upload.save()
                return Response({
                    'error': f'Failed to process file: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Upload.DoesNotExist:
            return Response({
                'error': 'Upload not found'
            }, status=status.HTTP_404_NOT_FOUND)
