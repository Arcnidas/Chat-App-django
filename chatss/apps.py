from django.apps import AppConfig


class ChatssConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatss'
    
    def ready(self):
        import chatss.signals 