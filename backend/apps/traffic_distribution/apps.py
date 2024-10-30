from django.apps import AppConfig


class TrafficDistributionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.traffic_distribution'
    verbose_name='Traffic Distribution'

    def ready(self):
        import apps.traffic_distribution.signals
