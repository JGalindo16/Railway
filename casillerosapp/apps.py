from django.apps import AppConfig


class CasillerosappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'casillerosapp'

    def ready(self):
        import casillerosapp.signals
