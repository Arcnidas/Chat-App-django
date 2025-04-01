from datetime import timedelta
from django.utils.timezone import now

class UpdateLastOnlineMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            threshold = now() - timedelta(minutes=1)
            if not request.user.last_online or request.user.last_online < threshold:
                request.user.last_online = now()
                request.user.save(update_fields=['last_online'])
        return self.get_response(request)
