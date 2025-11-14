from rest_framework import serializers
from .models import Webhook


class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = ['id', 'url', 'event_type', 'is_active', 'secret_key', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']