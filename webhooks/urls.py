from django.urls import path
from .views import WebhookListCreateView, WebhookRetrieveUpdateDestroyView, WebhookTestView

urlpatterns = [
    path('webhooks/', WebhookListCreateView.as_view(), name='webhook-list-create'),
    path('webhooks/<int:pk>/', WebhookRetrieveUpdateDestroyView.as_view(), name='webhook-detail'),
    path('webhooks/<int:pk>/test/', WebhookTestView.as_view(), name='webhook-test'),
]