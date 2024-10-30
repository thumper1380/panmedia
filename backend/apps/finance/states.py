from django.db import models
from django.utils.translation import gettext_lazy as _

class StatusChoices(models.TextChoices):
    DECLINED = 'DECLINED', _('Declined')
    NEW = 'NEW', _('New')
    PAYED = 'PAYED', _('Payed')
    SENT = 'SENT', _('Sent')