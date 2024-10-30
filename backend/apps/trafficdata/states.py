from django.db import models
from django.utils.translation import gettext_lazy as _


class StateChoices(models.TextChoices):
    CLICK = 'click',
    CLICK_LANDED = 'click_landed'
    LEAD = 'lead'
    LEAD_QUEUED = 'lead_queued'
    LEAD_PUSHED = 'lead_pushed'
    LEAD_DECLINED = 'lead_declined'
    SALE = 'sale'


class TrafficDataLogTypeChoices(models.TextChoices):
    STATE_SWITCHED = 'state_switched', _('State Switched')
    STATE_INITIATED = 'state_initiated', _('State Initiated')
    PUSHING_ERROR = 'pushing_error', _('Pushing Error')
    PUSHING_ATTEMPT = 'pushing_attempt', _('Pushing Attempt')

# TrafficDataLogTypeChoices.STATE_SWITCHED: '#ffc107',  # Yellow
# TrafficDataLogTypeChoices.STATE_INITIATED: '#28a745',  # Green
# TrafficDataLogTypeChoices.PUSHING_ERROR: '#dc3545',  # Red
# TrafficDataLogTypeChoices.PUSHING_ATTEMPT: '#007bff',  # Blue


class TrafficDataLogTypeColors(models.TextChoices):
    YELLOW = '#ffc107',  _('Yellow')  # Yellow
    GREEN = '#28a745',  _('Green')  # Green
    RED = '#dc3545',  _('Red')  # Red
    BLUE = '#007bff',  _('Blue')  # Blue


class TrafficDataLogColorChoices(models.TextChoices):
    SUCCESS = 'success', _('Success')
    WARNING = 'warning', _('Warning')
    DANGER = 'danger', _('Danger')


class QueueLeadStatusChoices(models.TextChoices):
    PENDING = 'pending', _('Pending')
    SUCCESS = 'success', _('Success')
    FAILED = 'failed', _('Failed')
    REVOKED = 'revoked', _('Revoked')


class PostbackStatusChoices(models.TextChoices):
    SUCCESS = 'success'
    PENDING = 'pending'
    ERROR = 'error'
    REVOKED = 'revoked'


class PostbackMethodChoices(models.TextChoices):
    GET = 'get', _('GET')
    POST = 'post', _('POST')
