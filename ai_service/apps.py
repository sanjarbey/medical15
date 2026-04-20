from django.apps import AppConfig

class AiServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_service'

    def ready(self):
        # Signallarni tizim ishga tushganda o'qitish
        import ai_service.signals