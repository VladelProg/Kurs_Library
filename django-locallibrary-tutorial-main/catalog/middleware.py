from .models import logs
from datetime import datetime

class LogUserActionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Логировать только если пользователь аутентифицирован
        if request.user.is_authenticated:
            # Добавляем запись в лог
            logs.objects.create(
                user=request.user,
                action=f"Visited {request.path}",
                timestamp=datetime.now()
            )

        return response