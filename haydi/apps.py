from django.apps import AppConfig

class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'haydi'

    def ready(self):
        import haydi.signals  # Sinyallerin yer aldığı dosyanın adını buraya yazın
