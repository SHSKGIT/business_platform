from django.utils import timezone
from datetime import timedelta


class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If the user is authenticated, set a session timeout of 5 minutes
        if request.user.is_authenticated:
            request.session.set_expiry(300)  # 300 seconds = 5 minutes

        response = self.get_response(request)
        return response


class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response
