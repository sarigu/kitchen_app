from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import logout

class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path_info.lstrip('/')
        if request.user.is_authenticated == False:  
            if not path in settings.EXCLUDED_URLS:   
                return redirect('login_app:login')