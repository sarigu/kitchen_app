from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import logout

class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        path = request.path_info.lstrip('/')
        # check if user is logged in
        if request.user.is_authenticated == False:  
            # check if url is in the list of excluded urls (urls everyone can access)
            if not path in settings.EXCLUDED_URLS:   
                return redirect('login_app:login')

        response = self.get_response(request)
        return response

