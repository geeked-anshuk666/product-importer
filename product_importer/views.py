from django.shortcuts import render
from django.http import JsonResponse
from uploads.models import Upload


def home(request):
    # Get recent uploads for display
    recent_uploads = Upload.objects.all().order_by('-created_at')[:10]
    return render(request, 'home.html', {'recent_uploads': recent_uploads})


def product_list(request):
    return render(request, 'product_list.html')


def webhook_list(request):
    return render(request, 'webhook_list.html')


def health_check(request):
    """
    Health check endpoint for Render and other monitoring services
    """
    return JsonResponse({'status': 'healthy', 'message': 'Application is running'})