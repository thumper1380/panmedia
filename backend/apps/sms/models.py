from django.db import models
# dj country
from django_countries.fields import CountryField
from apps.settings.models import CRMSettings
from django.db.models.signals import post_save
# import reciever
from django.dispatch import receiver

# Create your models here.
# import fields calidation no spaces, no special characters
from django.core.validators import RegexValidator
from apps.offer.models import Offer
import random
    
from django.template import Context, Template
from random import choice
import re
from django.utils.safestring import mark_safe
from django import template
register = template.Library()

@register.simple_tag
def random_word(words):
    word_list = words.split('|')
    return choice(word_list)




class SMSCampaign(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    country = CountryField(blank_label='(select country)', blank=True, null=True)
    # no spaces validation, no special characters
    sender = models.CharField(max_length=11, blank=True, null=True, validators=[RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')])    
    lists = models.ManyToManyField('SMSList')
    
    class Meta:
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'

    def get_offer(self):
        # retrieve offer according to weight
        offers = self.offers.all()
        total_weight = sum([offer.weight for offer in offers])
        random_weight = random.randint(0, total_weight)
        for offer in offers:
            random_weight -= offer.weight
            if random_weight <= 0:
                return offer.offer
            
    def get_offer_url(self):
        offer = self.get_offer()
        tracking_link = 'https://xam.manwin5.com/'
        return tracking_link
    

    def get_ad_text(self):
        # retrieve ad text according to weight
        ad_texts = self.ad_texts.all()
        total_weight = sum([ad_text.weight for ad_text in ad_texts])
        random_weight = random.randint(0, total_weight)
        for ad_text in ad_texts:
            random_weight -= ad_text.weight
            if random_weight <= 0:
                return ad_text
            
    @property
    def ad_text(self):
        template = self.get_ad_text()
        return template.render_message({'offer': self.get_offer_url()})

            
    




    def __str__(self):
        return self.name
    
class SMSCampaignOffer(models.Model):
    campaign = models.ForeignKey(SMSCampaign, on_delete=models.CASCADE, blank=True, null=True, related_name='offers')
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True, default=1,)
    class Meta:
        verbose_name = 'Campaign Offer'
        verbose_name_plural = 'Campaign Offers'


    def __str__(self):
        return self.campaign.name + ' - ' + self.offer.name





class SMSAdText(models.Model):
    campaign = models.ForeignKey(SMSCampaign, on_delete=models.CASCADE, blank=True, null=True, related_name='ad_texts')
    message = models.TextField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True, default=1)

    class Meta:
        verbose_name = 'Ad Text'
        verbose_name_plural = 'Ad Texts'

    def __str__(self):
        return f'{self.campaign.name} ad_#{self.id}'
    
    def render_message(self, context):
        message = self.message

        # Process word randomizer placeholders in the message template
        randomizer_pattern = r'\{\{\{([^{}]+)\}\}\}'
        message = re.sub(randomizer_pattern, lambda m: random_word(m.group(1)), message)

        # Replace variable placeholders in the message template
        template = Template(message)
        context = Context(context)
        message = template.render(context)

        return mark_safe(message)






class SMSList(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = 'List'
        verbose_name_plural = 'Lists'

    def __str__(self):
        return self.name


class SMSListData(models.Model):
    list = models.ForeignKey(SMSList, on_delete=models.CASCADE, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)

    is_valid = models.BooleanField(default=False, blank=True, null=True)

    class Meta:
        verbose_name = 'List Data'
        verbose_name_plural = 'List Data'

    def __str__(self):
        return f'{self.phone_number} - {self.first_name} {self.last_name}'


    @receiver(post_save, sender='sms.SMSListData')
    def validate_phone(sender, instance, created, **kwargs):
        neutrino = CRMSettings.neutrino()
        phone_number = instance.phone_number
        response = neutrino.phone_validate(number=phone_number)
        print(response)
        # if response['valid'] == True:
        #     instance.is_valid = True
        #     instance.save()




# import django mptt 
from mptt.models import MPTTModel, TreeForeignKey

class SMSAutomationCampaign(SMSCampaign):
    class Meta:
        proxy = True
        verbose_name = 'Automation'
        verbose_name_plural = 'Automation'

    def __str__(self):
        return self.name





class SMSAutomation(MPTTModel):
    campaign = models.ForeignKey(SMSAutomationCampaign, on_delete=models.CASCADE, blank=True, null=True, related_name='automations')
    delay = models.IntegerField(blank=True, null=True, default=1)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    class Meta:
        verbose_name = 'Automation'
        verbose_name_plural = 'Automations'

    def __str__(self):
        return f'{self.campaign.name} - {self.delay}'


class SMSAutomationTextAd(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    automation = models.ForeignKey(SMSAutomation, on_delete=models.CASCADE, blank=True, null=True, related_name='text_ads')

    class Meta:
        verbose_name = 'Automation Ad'
        verbose_name_plural = 'Automation Ads'

    def __str__(self):
        return self.name
