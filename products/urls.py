from django.urls import path
from .views import ProductListCreateView, ProductRetrieveUpdateDestroyView, ProductBulkDeleteView

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
    path('products/bulk-delete/', ProductBulkDeleteView.as_view(), name='product-bulk-delete'),
]