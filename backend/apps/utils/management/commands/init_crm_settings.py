from django.core.management.base import BaseCommand
from apps.settings.models import CRMSettings, SaleStatus
from django.conf import settings
from apps.offer.models import Offer
from .sale_status import sale_status_data

class Command(BaseCommand):
    help = 'Initializes the default CRMSettings'

    def handle(self, *args, **options):
        # init API offer if not exists
        # Offer.objects.get_or_create(name='API', alias='api', active=True, description='API offer', note='API offer', language='en')
        
        # init sale statuses if not exists\
        for sale_status in sale_status_data:
            SaleStatus.objects.update_or_create(key=sale_status['key'],
                defaults={
                    'name': sale_status['name'],
                    'description': sale_status['description'],
                    'color': sale_status['color']
                }
            )


        self.stdout.write(self.style.SUCCESS('Successfully initialized default CRMSettings'))
