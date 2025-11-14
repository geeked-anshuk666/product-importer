from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from webhooks.tasks import send_webhook_notification
from django.utils import timezone


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        sku = self.request.query_params.get('sku', None)
        name = self.request.query_params.get('name', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if sku:
            queryset = queryset.filter(sku__icontains=sku)
        if name:
            queryset = queryset.filter(name__icontains=name)
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
            
        return queryset
        
    def perform_create(self, serializer):
        product = serializer.save()
        
        # Send webhook notification
        payload = {
            'event': 'product_created',
            'product_id': product.id,
            'sku': product.sku,
            'name': product.name,
            'timestamp': timezone.now().isoformat()
        }
        send_webhook_notification.delay('product_imported', payload)


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def perform_update(self, serializer):
        product = serializer.save()
        
        # Send webhook notification
        payload = {
            'event': 'product_updated',
            'product_id': product.id,
            'sku': product.sku,
            'name': product.name,
            'timestamp': timezone.now().isoformat()
        }
        send_webhook_notification.delay('product_updated', payload)
        
    def perform_destroy(self, instance):
        product_id = instance.id
        product_sku = instance.sku
        product_name = instance.name
        
        # Send webhook notification before deletion
        payload = {
            'event': 'product_deleted',
            'product_id': product_id,
            'sku': product_sku,
            'name': product_name,
            'timestamp': timezone.now().isoformat()
        }
        send_webhook_notification.delay('product_deleted', payload)
        
        # Delete the product
        instance.delete()


class ProductBulkDeleteView(generics.GenericAPIView):
    def delete(self, request, *args, **kwargs):
        count = Product.objects.count()
        Product.objects.all().delete()
        
        # Send webhook notification
        payload = {
            'event': 'all_products_deleted',
            'count': count,
            'timestamp': timezone.now().isoformat()
        }
        send_webhook_notification.delay('all_products_deleted', payload)
        
        return Response(
            {'message': f'Successfully deleted {count} products'},
            status=status.HTTP_200_OK
        )
