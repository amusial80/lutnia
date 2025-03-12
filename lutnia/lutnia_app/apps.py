from django.apps import AppConfig


class LutniaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lutnia_app'

    def ready(self):
        import lutnia_app.signals