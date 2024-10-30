from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from .manager import QueueManagementManager
from .exceptions import QueueNotFound


class QueueManagementManager(models.Manager):
    def get_queue(self, country):
        try:
            return self.get(country=country, is_enabled=True)
        except ObjectDoesNotExist:
            raise QueueNotFound(f'Queue for {country} does not exist')
