from django.db import models


class Webhook(models.Model):
    WEBHOOK_EVENTS = [
        ('product_imported', 'Product Imported'),
        ('product_updated', 'Product Updated'),
        ('product_deleted', 'Product Deleted'),
        ('all_products_deleted', 'All Products Deleted'),
    ]
    
    url = models.URLField(max_length=500)
    event_type = models.CharField(max_length=50, choices=WEBHOOK_EVENTS)
    is_active = models.BooleanField(default=True)
    secret_key = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.event_type} -> {self.url}"
        
    class Meta:
        db_table = 'webhooks'
        indexes = [
            models.Index(fields=['event_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
