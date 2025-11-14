from rest_framework import serializers
from .models import Upload


class UploadSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Upload
        fields = ['id', 'file', 'status', 'total_rows', 'processed_rows', 'failed_rows', 
                  'progress_percentage', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'total_rows', 'processed_rows', 'failed_rows', 
                           'progress_percentage', 'created_at', 'updated_at']