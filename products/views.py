from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer


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


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductBulkDeleteView(generics.GenericAPIView):
    def delete(self, request, *args, **kwargs):
        count = Product.objects.count()
        Product.objects.all().delete()
        return Response(
            {'message': f'Successfully deleted {count} products'},
            status=status.HTTP_200_OK
        )
