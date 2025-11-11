from django.shortcuts import redirect
from django.urls import reverse

class AdminSuperuserOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_url = reverse('admin:index').replace('/index/', '/')
        if request.path.startswith(admin_url):
            if not request.user.is_authenticated or not request.user.is_superuser:
                return redirect('/')
        return self.get_response(request)
