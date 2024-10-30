from django.db import models
from django.conf import settings
# Create your models here.

from .states import StatusChoices
import random
import string

from apps.affiliate.models import Affiliate


class Invoice(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    # affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    from_date = models.DateField()
    to_date = models.DateField()
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.NEW)


    def generate_invoice_number(self):
        letters = string.ascii_uppercase
        numbers = string.digits
        return ''.join(random.choice(letters) for i in range(4)) + ''.join(random.choice(numbers) for i in range(4))

    def __str__(self):
        return f'{self.affiliate.email} - {self.amount}'
    
    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self.generate_invoice_number()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'