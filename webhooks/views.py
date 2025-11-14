from typing import TypeAlias


from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Webhook
from .serializers import WebhookSerializer
import requests
import logging

logger = logging.getLogger(__name__)


class WebhookListCreateView(generics.ListCreateAPIView):
    queryset = Webhook.objects.all()
    serializer_class = WebhookSerializer


class WebhookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Webhook.objects.all()
    serializer_class = WebhookSerializer


class WebhookTestView(generics.GenericAPIView):
    queryset = Webhook.objects.all()
    serializer_class: TypeAlias = WebhookSerializer
    
    def post(self, request, *args, **kwargs):
        webhook_id = kwargs.get('pk')
        try:
            webhook = Webhook.objects.get(id=webhook_id)
            
            # Send a test payload
            payload = {
                'event': 'test',
                'message': 'This is a test webhook',
                'timestamp': timezone.now().isoformat()
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            if webhook.secret_key:
                headers['X-Webhook-Secret'] = webhook.secret_key
            
            try:
                response = requests.post(webhook.url, json=payload, headers=headers, timeout=10)
                return Response({
                    'message': 'Webhook test sent successfully',
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                }, status=status.HTTP_200_OK)
            except requests.exceptions.RequestException as e:
                return Response({
                    'message': 'Failed to send webhook test',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Webhook.DoesNotExist:
            return Response({
                'error': 'Webhook not found'
            }, status=status.HTTP_404_NOT_FOUND)
