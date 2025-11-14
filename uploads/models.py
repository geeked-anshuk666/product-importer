from django.db import models
from django.contrib.auth.models import User


class Upload(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    file = models.FileField(upload_to='uploads/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_rows = models.IntegerField(default=0)
    processed_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"Upload {self.id} - {self.status}"
        
    @property
    def progress_percentage(self):
        if self.total_rows > 0:
            return round((self.processed_rows / self.total_rows) * 100, 2)
        return 0
        
    class Meta:
        db_table = 'uploads'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
