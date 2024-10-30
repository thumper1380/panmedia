from django.apps import AppConfig


class UtilsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.utils'
    verbose_name = 'Utils'

    def ready(self):
        import apps.utils.signals