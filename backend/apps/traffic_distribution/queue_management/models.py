
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django.core.validators import MinValueValidator, MaxValueValidator
from .choices import DayChoices
from .manager import QueueManagementManager
from .exceptions import QueueManagementException


class QueueManagement(models.Model):

    objects = QueueManagementManager()

    country = CountryField(unique=True)
    from_hour = models.TimeField()
    to_hour = models.TimeField()
    from_day = models.IntegerField(
        choices=DayChoices.choices, default=DayChoices.MONDAY)
    to_day = models.IntegerField(
        choices=DayChoices.choices, default=DayChoices.SUNDAY)
    is_enabled = models.BooleanField('Enabled', default=True)

    thank_you_url = models.URLField(
        'Thank You URL', blank=True, null=True, help_text='URL to redirect the user after the lead is created')

    min_interval = models.IntegerField(
        'Min Interval', default=0, help_text='The minimum interval between two leads in minutes', validators=[MinValueValidator(0)])

    max_interval = models.IntegerField(
        'Max Interval', default=0, help_text='The maximum interval between two leads in minutes', validators=[MinValueValidator(0)])

    filter_rate = models.IntegerField(
        'Filter Rate (%)', default=100, help_text='The percentage of the leads that will get into the queue.\n100 means all the leads will get into the queue.\n0 means the leads will be send to rotation tree', validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        verbose_name = 'Queue Management'
        verbose_name_plural = 'Queue Management'

    def __str__(self):
        return f'{self.country} - {self.from_hour} - {self.to_hour} - {self.from_day} - {self.to_day}'

    def clean(self):
        if self.from_hour >= self.to_hour:
            raise QueueManagementException('from_hour must be less than to_hour')
