from django.apps import AppConfig


class TrafficDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.trafficdata'
    verbose_name: str = 'Traffic Data'


    def ready(self):
        import apps.trafficdata.signals