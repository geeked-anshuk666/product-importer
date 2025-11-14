from django.urls import path
from .views import UploadCreateView, UploadProgressView, ProcessUploadView, upload_stats

urlpatterns = [
    path('uploads/', UploadCreateView.as_view(), name='upload-create'),
    path('uploads/<int:pk>/', UploadProgressView.as_view(), name='upload-progress'),
    path('uploads/<int:pk>/process/', ProcessUploadView.as_view(), name='upload-process'),
    path('uploads/stats/', upload_stats, name='upload-stats'),
]