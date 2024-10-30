from django.db import models
from django_countries.fields import CountryField
from apps.settings.models import Form
import string
import random
# import money field
from djmoney.models.fields import MoneyField, Money
from apps.traffic_distribution.models import Advertiser

# Create your models here.


class OfferCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Offer Category'
        verbose_name_plural = 'Offer Categories'

class Offer(models.Model):
    class RedirectType(models.TextChoices):
        HTTP_REDIRECT, META_REDIRECT, JAVASCRIPT_REDIRECT, REDIRECT_WITHOUT_REFERER = 'HTTP', 'META', 'JAVASCRIPT', 'REDIRECT_WITHOUT_REFERER'

    name = models.CharField(max_length=255)
    language = models.CharField(blank=True, max_length=30)
    lead_form = models.ForeignKey(Form, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    alias = models.CharField(max_length=10, unique=True, blank=True, null=True)
    redirect_type = models.CharField(max_length=30, choices=RedirectType.choices, default=RedirectType.HTTP_REDIRECT)
    cpa = MoneyField('CPA', max_digits=14, decimal_places=2, default_currency='USD', default=Money(0, 'USD'), help_text='Cost per action')
    revenue = MoneyField('Revenue', max_digits=14, decimal_places=2, default_currency='USD', default=Money(0, 'USD'), help_text='Revenue per action')
    allowed_countries = CountryField(multiple=True,)
    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE, null=True, blank=True, help_text='Default advertiser for this offer.')
    category = models.ForeignKey(OfferCategory, on_delete=models.CASCADE, null=True, blank=True, help_text='Category for this offer.')
    # allowed_counties - list of countries that are allowed to see the offer
    # cpa - cost per action - how much the affiliate will get paid for each action
    # creative assets - images, videos, etc. - for the affiliate to use in his marketing campaign for this offer (optional)


    def __str__(self):
        return self.name

    def generate_random_string(self):
        """
        generate random string used as alias for offer, the string is 1-7 characters long.
        contains only uppercase letters, lowercase letters.
        the string is unique in the database.
        """
        while True:
            alias = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=random.randint(5, 10)))
            if not Offer.objects.filter(alias=alias).exists():
                return alias

    def save(self, *args, **kwargs):
        if not self.alias:
            self.alias = self.generate_random_string()
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'





# class ShortLink(models.Model):
#     """
#     Short link for offer landing page - used in the affiliate marketing campaign
#     """ 
#     offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     active = models.BooleanField(default=True)
#     note = models.TextField(blank=True, null=True)
    