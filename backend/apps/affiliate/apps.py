from django.apps import AppConfig


class AffiliateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.affiliate'
    verbose_name: str = 'Affiliates'

    def ready(self):
        import apps.affiliate.signals
        from apps.trafficdata.models import TrafficData