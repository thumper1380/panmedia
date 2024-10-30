from django.db import models

# Create your models here.





class EmailServer(models.Model):
    class SpeedLimit(models.IntegerChoices):
        # 5 emails per hour, 10 emails per hour, 100 emails per hour, 1000 emails per hour, 10000 emails per hour, 100000 emails per hour
        FIVE = 5
        TEN = 10
        HUNDRED = 100
        THOUSAND = 1000
        TEN_THOUSAND = 10000
        HUNDRED_THOUSAND = 100000


    name = models.CharField(max_length=255, blank=True, null=True)
    speed_limit = models.IntegerField(choices=SpeedLimit.choices, default=SpeedLimit.FIVE, blank=True, null=True, help_text='How many emails can be sent per hour')
    host = models.CharField(max_length=255, blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Email Server'
        verbose_name_plural = 'Email Servers'