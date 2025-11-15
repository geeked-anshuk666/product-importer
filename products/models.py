from django.db import models


class Product(models.Model):
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['id']  # Maintain consistent ordering by ID
