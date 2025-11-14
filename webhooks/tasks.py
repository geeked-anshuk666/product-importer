from celery import shared_task
from .models import Webhook
import requests
import json
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_webhook_notification(event_type, payload):
    """
    Send webhook notifications for events
    """
    try:
        # Get all active webhooks for this event type
        webhooks = Webhook.objects.filter(event_type=event_type, is_active=True)
        
        results = []
        
        for webhook in webhooks:
            try:
                headers = {
                    'Content-Type': 'application/json'
                }
                
                if webhook.secret_key:
                    headers['X-Webhook-Secret'] = webhook.secret_key
                
                response = requests.post(
                    webhook.url, 
                    json=payload, 
                    headers=headers, 
                    timeout=10
                )
                
                results.append({
                    'webhook_id': webhook.id,
                    'status_code': response.status_code,
                    'success': response.status_code in [200, 201, 202, 204]
                })
                
                logger.info(f"Webhook {webhook.id} sent successfully: {response.status_code}")
                
            except requests.exceptions.RequestException as e:
                results.append({
                    'webhook_id': webhook.id,
                    'error': str(e),
                    'success': False
                })
                
                logger.error(f"Failed to send webhook {webhook.id}: {str(e)}")
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to process webhooks for event {event_type}: {str(e)}")
        return {'error': str(e)}