from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from .models import Upload
from .serializers import UploadSerializer
from .tasks import process_csv_upload


class UploadCreateView(generics.CreateAPIView):
    queryset = Upload.objects.all()
    serializer_class = UploadSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def perform_create(self, serializer):
        # Save the upload record
        upload = serializer.save()
        
        # Trigger the Celery task to process the file asynchronously
        process_csv_upload.delay(upload.id)
        
        
class UploadProgressView(generics.RetrieveAPIView):
    queryset = Upload.objects.all()
    serializer_class = UploadSerializer
    
    
class ProcessUploadView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        # This endpoint is kept for backward compatibility
        # but the processing is now done asynchronously via Celery
        return Response({
            'message': 'Upload processing started asynchronously'
        }, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
def upload_stats(request):
    """
    Get upload statistics
    """
    total = Upload.objects.count()
    completed = Upload.objects.filter(status='completed').count()
    processing = Upload.objects.filter(status='processing').count()
    failed = Upload.objects.filter(status='failed').count()
    
    return Response({
        'total': total,
        'completed': completed,
        'processing': processing,
        'failed': failed
    })