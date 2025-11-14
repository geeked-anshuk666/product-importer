from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def product_list(request):
    return render(request, 'product_list.html')


def webhook_list(request):
    return render(request, 'webhook_list.html')