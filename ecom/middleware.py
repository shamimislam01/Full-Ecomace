# middleware.py
from django.shortcuts import render
from django.conf import settings

class Force404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # যদি 404 হয় এবং DEBUG=True হয়
        if response.status_code == 404 and settings.DEBUG:
            return render(request, '404.html', status=404)

        return response
