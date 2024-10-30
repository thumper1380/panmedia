from apps.trafficdata.states import StateChoices

from apps.utils.folders import (AdvertiserFolder, AffiliateFolder, CountryFolder,
                                Folder, Management,
                                TargetFolder)

from datetime import datetime, timedelta
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.mail.backends.smtp import EmailBackend
from django.core.validators import MaxValueValidator, MinValueValidator, validate_email
from django_countries.fields import CountryField
from djmoney.models.fields import Money
from django.db import models
from django.template import Context, Template
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import numexpr as ne
import phonenumbers
import random
import re
from django.conf import settings
import hashlib
import dns.resolver
import dns.exception

from polymorphic_tree.managers import PolymorphicMPTTQuerySet


from .exceptions import (EmailAddressException, FieldException, FormException, LeadProfileException,
                         PhoneNumberException, SMSFolderException, TextInputException)
from apps.trafficdata.states import QueueLeadStatusChoices
# Create your models here.


from .neutrino import Neutrino


class SaleStatus(models.Model):
    COLOR_CHOICES = (('#90E623', 'Light Green'), ('#00FF00', 'Green'), ('#FFFF00', 'Yellow'), ('#FFA500', 'Orange'), ('#FF0000', 'Red'), ('#FF0000', 'Light Red'), ('#0000FF', 'Blue'), ('#00FFFF', 'Light Blue'), ('#800080', 'Purple'), ('#FFC0CB', 'Pink'), ('#000000', 'Black'), ('#FFFFFF', 'White'), ('#808080', 'Grey'), ('#A52A2A', 'Brown'), ('#FFD700', 'Gold'), ('#C0C0C0', 'Silver'), ('#B87333', 'Copper'), ('#CD7F32', 'Bronze'), ('#E5E4E2', 'Platinum'), ('#D2D7D3', 'Titanium'), ('#A9ACB6', 'Aluminum'), ('#B0C4DE', 'Steel'), ('#D4D4D4', 'Chrome'), ('#FF00FF', 'Magenta'), ('#00FFFF', 'Cyan'), ('#00FF00', 'Lime'), ('#800000', 'Maroon'), ('#000080', 'Navy'), ('#808000',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       '#Olive'), ('#008080', 'Teal'), ('#7FFFD4', 'Aquamarine'), ('#40E0D0', 'Turquoise'), ('#EE82EE', 'Violet'), ('#4B0082', 'Indigo'), ('#6A5ACD', 'Slate Blue'), ('#708090', 'Slate Grey'), ('#2F4F4F', 'Slate Black'), ('#F5F5F5', 'Slate White'), ('#8B4513', 'Slate Brown'), ('#FF8C00', 'Slate Orange'), ('#8B0000', 'Slate Red'), ('#2E8B57', 'Slate Green'), ('#9ACD32', 'Slate Yellow'), ('#9370DB', 'Slate Purple'), ('#FF69B4', 'Slate Pink'), ('#00FFFF', 'Slate Cyan'), ('#FF00FF', 'Slate Magenta'), ('#00FF00', 'Slate Lime'), ('#800000', 'Slate Maroon'), ('#000080', 'Slate Navy'), ('#808000', 'Slate Olive'), ('#008080', 'Slate Teal'), ('#7FFFD4', 'Slate Aquamarine'))

    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=100, unique=True)
    key = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=100, choices=COLOR_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Sale Status'
        verbose_name_plural = 'Sale Statuses'


# phoonenumbers
# import validate_email


class LeadProfile(models.Model):
    class AutoCompleteChoices(models.TextChoices):
        OFF = 'off', _('Off')
        ON = 'on', _('On')
        GIVEN_NAME = 'given-name', _('Given Name')
        FAMILY_NAME = 'family-name', _('Family Name')
        EMAIL = 'email', _('Email')
        USERNAME = 'username', _('Username')
        NEW_PASSWORD = 'new-password', _('New Password')
        CURRENT_PASSWORD = 'current-password', _('Current Password')
        ONE_TIME_CODE = 'one-time-code', _('One Time Code')
        ORGANIZATION = 'organization', _('Organization')
        STREET_ADDRESS = 'street-address', _('Street Address')
        ADDRESS_LINE1 = 'address-line1', _('Address Line 1')
        ADDRESS_LINE2 = 'address-line2', _('Address Line 2')
        ADDRESS_LINE3 = 'address-line3', _('Address Line 3')
        ADDRESS_LEVEL4 = 'address-level4', _('Address Level 4')
        ADDRESS_LEVEL3 = 'address-level3', _('Address Level 3')
        ADDRESS_LEVEL2 = 'address-level2', _('Address Level 2')
        ADDRESS_LEVEL1 = 'address-level1', _('Address Level 1')
        COUNTRY = 'country', _('Country')
        COUNTRY_NAME = 'country-name', _('Country Name')
        POSTAL_CODE = 'postal-code', _('Postal Code')
        CC_NAME = 'cc-name', _('CC Name')
        CC_GIVEN_NAME = 'cc-given-name', _('CC Given Name')
        CC_ADDITIONAL_NAME = 'cc-additional-name', _('CC Additional Name')
        CC_FAMILY_NAME = 'cc-family-name', _('CC Family Name')
        CC_NUMBER = 'cc-number', _('CC Number')
        CC_EXP = 'cc-exp', _('CC Exp')
        CC_EXP_MONTH = 'cc-exp-month', _('CC Exp Month')
        CC_EXP_YEAR = 'cc-exp-year', _('CC Exp Year')
        CC_CSC = 'cc-csc', _('CC CSC')
        CC_TYPE = 'cc-type', _('CC Type')
        TRANSACTION_CURRENCY = 'transaction-currency', _(
            'Transaction Currency')
        TRANSACTION_AMOUNT = 'transaction-amount', _('Transaction Amount')
        LANGUAGE = 'language', _('Language')
        BDAY = 'bday', _('Bday')
        BDAY_DAY = 'bday-day', _('Bday Day')
        BDAY_MONTH = 'bday-month', _('Bday Month')
        BDAY_YEAR = 'bday-year', _('Bday Year')
        SEX = 'sex', _('Sex')
        TEL = 'tel', _('Tel')
        TEL_COUNTRY_CODE = 'tel-country-code', _('Tel Country Code')
        TEL_NATIONAL = 'tel-national', _('Tel National')
        TEL_AREA_CODE = 'tel-area-code', _('Tel Area Code')
        TEL_LOCAL = 'tel-local', _('Tel Local')
        TEL_LOCAL_PREFIX = 'tel-local-prefix', _('Tel Local Prefix')
        TEL_LOCAL_SUFFIX = 'tel-local-suffix', _('Tel Local Suffix')
        TEL_EXTENSION = 'tel-extension', _('Tel Extension')
        IMPP = 'impp', _('Impp')
        URL = 'url', _('Url')
        PHOTO = 'photo', _('Photo')

    class FieldTypeChoices(models.TextChoices):
        TEXT = 'text', _('Text')
        TEXTAREA = 'textarea', _('Textarea')
        EMAIL = 'email', _('Email')
        URL = 'url', _('Url')
        TEL = 'tel', _('Tel')
        NUMBER = 'number', _('Number')
        RANGE = 'range', _('Range')
        DATE = 'date', _('Date')
        MONTH = 'month', _('Month')
        WEEK = 'week', _('Week')
        TIME = 'time', _('Time')
        DATETIME_LOCAL = 'datetime-local', _('Datetime Local')
        COLOR = 'color', _('Color')
        CHECKBOX = 'checkbox', _('Checkbox')
        RADIO = 'radio', _('Radio')
        FILE = 'file', _('File')
        HIDDEN = 'hidden', _('Hidden')
        IMAGE = 'image', _('Image')
        BUTTON = 'button', _('Button')
        SUBMIT = 'submit', _('Submit')
        RESET = 'reset', _('Reset')

    type = models.CharField(
        'Type', max_length=255, choices=FieldTypeChoices.choices, default=FieldTypeChoices.TEXT)
    label = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    place_holder = models.CharField(
        'Place Holder', max_length=255, blank=True, null=True)
    autocomplete = models.CharField(
        'Auto Complete', max_length=255, choices=AutoCompleteChoices.choices, default=AutoCompleteChoices.OFF)
    pattern = models.CharField(
        'Pattern', max_length=255, blank=True, null=True)
    position = models.PositiveIntegerField(default=0)
    # step = models.ForeignKey(
    #     'Step', on_delete=models.CASCADE, related_name='fields')

    validation_rules = models.ManyToManyField(
        'ValidationRule', related_name='fields', blank=True)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = 'Lead Profile'
        verbose_name_plural = 'Lead Profile'
        # unique_together = [('key', 'form'), ('position', 'form')]
        ordering = ['position']


class ValidationRule(models.Model):
    """Model definition for ValidationRule."""
    class RuleTypes(models.TextChoices):
        LENGTH = 'length', _('Length')
        FORMAT = 'format', _('Format')
        RANGE = 'range', _('Range')
        REQUIRED = 'required', _('Required')
        EMAIL = 'email', _('Email')
        PHONE = 'phone', _('Phone')

    name = models.CharField(max_length=255)
    rule_type = models.CharField(
        'Rule Type', max_length=255, choices=RuleTypes.choices, default=RuleTypes.LENGTH)
    rule_parameters = models.JSONField(null=True, blank=True)

    class Meta:
        """Meta definition for ValidationRule."""

        verbose_name = 'ValidationRule'
        verbose_name_plural = 'ValidationRules'

    def __str__(self):
        """Unicode representation of ValidationRule."""
        return self.rule_type.title()
    
    def get_validator_by_field(self, field):
        from rest_framework.serializers import EmailField, CharField, IntegerField
        if self.rule_type == self.RuleTypes.REQUIRED:
            return CharField(required=True)
        elif self.rule_type == self.RuleTypes.LENGTH:
            return CharField(max_length=self.rule_parameters.get('max'), min_length=self.rule_parameters.get('min'))

    def validate(self, value):
        if self.rule_type == self.RuleTypes.REQUIRED:
            if not value:
                raise FieldException('This field is required')
        elif self.rule_type == self.RuleTypes.LENGTH:
            if len(value) < self.rule_parameters.get('min'):
                raise FieldException(
                    f'Value must be at least {self.rule_parameters.get("min")} characters long')
            if len(value) > self.rule_parameters.get('max'):
                raise FieldException(
                    f'Value must be at most {self.rule_parameters.get("max")} characters long')
        elif self.rule_type == self.RuleTypes.FORMAT:
            if not re.match(self.rule_parameters.get('regex'), value):
                raise FieldException(
                    f'Value must match {self.rule_parameters.get("regex")}')
        elif self.rule_type == self.RuleTypes.RANGE:
            if value < self.rule_parameters.get('min'):
                raise FieldException(
                    f'Value must be at least {self.rule_parameters.get("min")}')
            if value > self.rule_parameters.get('max'):
                raise FieldException(
                    f'Value must be at most {self.rule_parameters.get("max")}')
        elif self.rule_type == self.RuleTypes.EMAIL:
            try:
                validate_email(value)
            except ValidationError as e:
                raise FieldException(str(e.message))
        elif self.rule_type == self.RuleTypes.PHONE:
            try:
                phone = phonenumbers.parse(value, None)
                if not phonenumbers.is_valid_number(phone):
                    raise FieldException(f'Invalid phone number')
            except phonenumbers.NumberParseException:
                raise FieldException(f'Invalid phone number')
        else:
            raise FieldException(
                f'Validation rule {self.rule_type} is not supported')


class Form(models.Model):
    name = models.CharField(max_length=255)
    header = models.CharField(max_length=255)
    submit_button_text = models.CharField(max_length=100)
    toc = models.BooleanField(
        default=False, verbose_name='Terms and Conditions, Privacy Policy')
    fields = models.ManyToManyField(
        'LeadProfile', related_name='forms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta definition for Form."""

        verbose_name = 'Form'
        verbose_name_plural = 'Forms'

    def get_field(self, key):
        return self.fields.get(key=key)

    def validate(self, **kwargs):
        errors = {}
        for key, value in kwargs.items():
            try:
                field = self.get_field(key)
            except LeadProfile.DoesNotExist:
                continue
            # if field.validation_rules.filter(rule_type=ValidationRule.RuleTypes.REQUIRED).exists() and not value:
            #     errors[key] = 'This field is required'
            for rule in field.validation_rules.all():
                try:
                    rule.validate(value)
                except FieldException as e:
                    errors[key] = str(e)

        print(errors)

        if errors:
            raise FormException(errors=errors)

    def __str__(self):
        return f'{self.name} / {self.header}'


class GoalType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Goal(models.Model):
    state = models.CharField(max_length=255, choices=StateChoices.choices)
    goal_type = models.ForeignKey(
        'GoalType', on_delete=models.CASCADE, related_name='goals')
    force_sale_status = models.ForeignKey(
        SaleStatus, on_delete=models.CASCADE, related_name='goals', null=True, blank=True)

    def __str__(self):
        return f'{self.goal_type}'


HANDLER_TYPES = (('sale', 'Sale'), ('push', 'Push'), ('form-push', 'Form Push'), ('form', 'Form'), ('advertiser-declined',
                 'Advertiser Declined'), ('advertiser-accepted', 'Advertiser Accepted'), ('impression', 'Impression'))


COLOR_CHOICES = (('#00ff00', 'Light Green'), ('#ff0000', 'Light Red'), ('#0000ff', 'Light Blue'), ('#ffff00', 'Light Yellow'), ('#ff00ff', 'Light Magenta'), ('#00ffff', 'Light Cyan'), ('#000000', 'Black'), ('#ffffff', 'White'), ('#800000', 'Maroon'), ('#ff00ff', 'Fuchsia'), ('#800080', 'Purple'), ('#000080', 'Navy'), ('#808000', 'Olive'), ('#008080', 'Teal'), ('#008000', 'Green'), ('#00ffff', 'Aqua'), ('#0000ff', 'Blue'), ('#00ff00', 'Lime'), ('#ff0000', 'Red'), ('#c0c0c0', 'Silver'), ('#808080', 'Gray'), ('#800000', 'Dark Red'), ('#ff00ff', 'Dark Magenta'), ('#800080', 'Dark Purple'), ('#000080', 'Dark Blue'), ('#808000', 'Dark Olive Green'), ('#008080', 'Dark Cyan'), ('#008000', 'Dark Green'), ('#00ffff', 'Dark Aqua'), ('#0000ff', 'Dark Blue'),
                 ('#00ff00', 'Dark Lime'), ('#ff0000', 'Dark Red'), ('#c0c0c0', 'Dark Silver'), ('#808080', 'Dark Gray'), ('#9999ff', 'Pale Blue'), ('#993366', 'Brown'), ('#ffffcc', 'Pale Yellow'), ('#ccffff', 'Pale Cyan'), ('#660066', 'Dark Purple'), ('#ff8080', 'Salmon'), ('#0066cc', 'Royal Blue'), ('#ccccff', 'Light Purple'), ('#000080', 'Midnight Blue'), ('#ff00ff', 'Pink'), ('#ffff00', 'Yellow'), ('#00ffff', 'Cyan'), ('#800080', 'Purple'), ('#800000', 'Maroon'), ('#008080', 'Teal'), ('#0000ff', 'Blue'), ('#00ccff', 'Sky Blue'), ('#ccffff', 'Light Cyan'), ('#ccffcc', 'Pale Green'), ('#ffff99', 'Light Yellow'), ('#99ccff', 'Light Sky Blue'), ('#ff99cc', 'Light Pink'), ('#cc99ff', 'Plum'), ('#ffcc99', 'Peach'), ('#3366ff', 'Royal Blue'), ('#33cccc', 'Turquoise'),)


class Source(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=255, choices=COLOR_CHOICES)
    icon = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class State(models.Model):
    key = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    handler_type = models.CharField(max_length=255)
    lead_flow = models.ForeignKey('LeadFlow', on_delete=models.CASCADE)
    handler_type = models.CharField(max_length=255, choices=HANDLER_TYPES)
    color = models.CharField(max_length=255, choices=COLOR_CHOICES)

    class Meta:
        """Meta definition for State."""

        verbose_name = 'State'
        verbose_name_plural = 'States'

    def __str__(self):
        return self.key


class Transition(models.Model):
    from_state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='from_state')
    to_state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='to_state')
    lead_flow = models.ForeignKey('LeadFlow', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        """Meta definition for Transition."""

        verbose_name = 'Transition'
        verbose_name_plural = 'Transitions'

    def __str__(self):
        return f'{self.from_state} => {self.to_state}'


class LeadFlow(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        """Meta definition for LeadFlow."""

        verbose_name = 'Lead Flow'
        verbose_name_plural = 'Lead Flows'

    def __str__(self):
        transition_str = list(self.transition_set.all())
        transition_str = ' => '.join(
            [str(transition) for i, transition in enumerate(transition_str) if i % 2 == 0])
        return f'{self.name}: {transition_str.upper()}'


class CRMTermQuerySet(models.QuerySet):
    def calculate(self, context, **kwargs):
        terms = []
        for term in self.filter(**kwargs).order_by('order'):
            value = term.calculate_value(context)
            terms.append(
                {'title': term.label, 'value': value, 'icon': term.icon, 'type': term.type})
        return terms


class CRMTerm(models.Model):
    class TypeChoices(models.TextChoices):
        MONEY = 'MONEY', _('Money')
        PERCENTAGE = 'PERCENTAGE', _('Percentage')
        NUMBER = 'NUMBER', _('Number')

    label = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    icon = models.CharField(max_length=255, blank=True, null=True)
    formula = models.TextField(blank=True, null=True)
    type = models.CharField(
        max_length=20, choices=TypeChoices.choices, default=TypeChoices.NUMBER)
    description = models.CharField(max_length=255, blank=True, null=True)
    objects = CRMTermQuerySet.as_manager()

    class Meta:
        """Meta definition for CRMTerms."""

        verbose_name = 'CRM Term'
        verbose_name_plural = 'CRM Terms'

    def __str__(self):
        return f'{self.label} / {self.id}'

    def calculate_value(self, context):
        template = Template(self.formula)
        value = template.render(Context(context))
        # calculate the value using numexpr
        try:
            value = ne.evaluate(value)
            return value
        except Exception as e:
            return 0 
        # except ZeroDivisionError:
        #     return 0

class CustomEmailBackend(EmailBackend):
    def __init__(self, *args, **kwargs):
        try:
            settings: EmailSettings = CRMSettings.objects.email_backend()
            if settings is None:
                raise ImproperlyConfigured('No EmailSettings configured')
        except ImproperlyConfigured:
            raise
        except Exception as e:
            raise ImproperlyConfigured(
                'Error retrieving EmailSettings: %s' % e)

        kwargs['host'] = settings.host
        kwargs['port'] = settings.port
        kwargs['username'] = settings.username
        kwargs['password'] = settings.password
        kwargs['use_tls'] = settings.use_tls

        super().__init__(*args, **kwargs)


class EmailSettings():
    def __init__(self, host, port, username, password, use_tls):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls


class EmailTemplate(models.Model):
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()

    class Meta:
        """Meta definition for EmailTemplate."""

        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'

    def __str__(self):
        return self.name

    def send(self, to, context, html=False):
        from django.template import Template, Context
        from django.core.mail import EmailMessage
        from django.core.mail import EmailMultiAlternatives

        template = Template(self.body)
        body = template.render(Context(context))

        email = EmailMultiAlternatives(
            subject=self.subject,
            body=body,
            from_email=CRMSettings.DEFAULT_FROM_EMAIL,
            to=to,
        )

        email.attach_alternative(body, 'text/html')
        email.send()


# class CRMSettingsManager(models.Manager):
#     def get(self, key):
#         try:
#             return self.get_queryset().get(key=key).value
#         except self.model.DoesNotExist:
#             return None

#     def time_zone(self):
#         return self.get(self.model.TIME_ZONE) or 'UTC'

#     def time_format(self):
#         return self.get(self.model.TIME_FORMAT) or '%Y-%m-%d %H:%M:%S %Z%z'

#     def neutrino_user_id(self):
#         return self.get(self.model.NEUTRINO_USER_ID)

#     def neutrino_api_key(self):
#         return self.get(self.model.NEUTRINO_API_KEY)

#     def neutrino_base_url(self):
#         return self.get(self.model.NEUTRINO_BASE_URL)

#     def neutrino(self) -> Neutrino:
#         user_id, api_key, base_url = self.neutrino_user_id(
#         ), self.neutrino_api_key(), self.neutrino_base_url()
#         if not user_id or not api_key or not base_url:
#             return None

#         neutruno = Neutrino(**{
#             'user_id': user_id,
#             'api_key': api_key,
#             'base_url': base_url,
#         })

#         return neutruno

#     def email_backend(self) -> EmailSettings:
#         email_host = self.get(self.model.EMAIL_HOST)
#         email_port = int(self.get(self.model.EMAIL_PORT))
#         email_username = self.get(self.model.EMAIL_HOST_USER)
#         email_password = self.get(self.model.EMAIL_HOST_PASSWORD)
#         email_use_tls = bool(self.get(self.model.EMAIL_USE_TLS))

#         if not email_host or not email_port or not email_username or not email_password or not email_use_tls:
#             return None

#         return EmailSettings(**{
#             'host': email_host,
#             'port': email_port,
#             'username': email_username,
#             'password': email_password,
#             'use_tls': email_use_tls,
#         })

#     def default_time_range(self):
#         return self.get(self.model.DEFAULT_TIME_RANGE)

#     def push_lead_max_retries(self):
#         return int(self.get(self.model.PUSH_LEAD_MAX_RETRIES)) if self.get(self.model.PUSH_LEAD_MAX_RETRIES) != None else self.model.DEFAULT_PUSH_LEAD_MAX_RETRIES

#     def default_time_frame(self):
#         return self.get(self.model.DEFAULT_TIME_FRAME)

#     def uniqueness_ttl(self) -> int:
#         # get the uniqueness ttl in hours
#         self.model: CRMSettings
#         return int(self.get(self.model.UNIQUENESS_TTL)) if self.get(self.model.UNIQUENESS_TTL) != None else self.model.DEFAULT_UNIQUENESS_TTL

#     def token_ttl(self) -> int:
#         # get the token ttl in hours
#         self.model: CRMSettings
#         return float(self.get(self.model.TOKEN_TTL)) if self.get(self.model.TOKEN_TTL) != None else self.model.DEFAULT_TOKEN_TTL


class CRMSettings(models.Model):

    class TimeZoneChoices(models.TextChoices):
        UTC = 'UTC', 'Coordinated Universal Time'
        EST = 'EST', 'Eastern Standard Time'
        CST = 'CST', 'Central Standard Time'

    class TimeFormatChoices(models.TextChoices):
        DEFAULT = '%Y-%m-%d %H:%M:%S %Z%z', 'Default'
        SHORT = '%Y-%m-%d %H:%M:%S', 'Short'
        LONG = '%A, %d %B, %Y %H:%M:%S', 'Long'

    time_zone = models.CharField(
        max_length=255, choices=TimeZoneChoices.choices, default=TimeZoneChoices.UTC)

    time_format = models.CharField(
        max_length=255, choices=TimeFormatChoices.choices, default=TimeFormatChoices.DEFAULT)

    # Neutrino settings

    neutrino_user_id = models.CharField(max_length=255, null=True, blank=True)
    neutrino_api_key = models.CharField(max_length=255, null=True, blank=True)
    neutrino_base_url = models.CharField(max_length=255, null=True, blank=True)

    #

    default_time_range = models.IntegerField(null=True, blank=True)
    push_lead_max_retries = models.IntegerField(default=10)
    default_time_frame = models.CharField(
        max_length=255, null=True, blank=True)
    uniqueness_ttl = models.IntegerField(default=24)
    token_ttl = models.IntegerField(default=7 * 24)

    # Email settings
    email_host = models.CharField(max_length=255, null=True, blank=True)
    email_port = models.IntegerField(null=True, blank=True)
    email_host_user = models.CharField(max_length=255, null=True, blank=True)
    email_host_password = models.CharField(
        max_length=255, null=True, blank=True)
    email_use_tls = models.BooleanField(default=True)

    default_from_email = models.EmailField(default='testemail@mail.com')

    class Meta:
        verbose_name = 'CRM Setting'
        verbose_name_plural = 'CRM Settings'

    def clean(self):
        if not self.pk and CRMSettings.objects.exists():
            raise ValidationError(
                'There is can be only one CRM Settings instance')

    def __str__(self):
        return 'CRM Settings'

    # load
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    @classmethod
    def neutrino(cls):
        settings = cls.load()
        return Neutrino(user_id=settings.neutrino_user_id, api_key=settings.neutrino_api_key, base_url=settings.neutrino_base_url)

    @classmethod
    def get(cls, key):
        return getattr(cls.load(), key)


class RiskManagementQuerySet(PolymorphicMPTTQuerySet):
    ...


class RiskManagement(Folder, Management):
    objects = RiskManagementQuerySet.as_manager()

    class Meta:
        """Meta definition for RiskManagement."""
        verbose_name = 'Risk Management'
        verbose_name_plural = 'Risk Managements'


class RiskManagementAdvertiserFolder(RiskManagement, AdvertiserFolder):
    ...


class RiskManagementAffiliateFolder(RiskManagement, AffiliateFolder):
    ...


class RiskManagementCountryFolder(RiskManagement, CountryFolder):
    ...


class RiskFolder(TargetFolder, RiskManagement):
    class StrategyChoices(models.TextChoices):
        AMOUNT = 'amount', 'Amount'
        PERCENTAGE = 'percentage', 'Percentage'

    state = models.CharField(
        max_length=255, choices=TargetFolder.StateChoices.choices, default=TargetFolder.StateChoices.CLICK)
    strategy = models.CharField(
        max_length=255, choices=StrategyChoices.choices, default=StrategyChoices.AMOUNT)
    value = models.PositiveIntegerField(default=0)

    current_value = models.PositiveIntegerField(default=0)

    class Meta:
        """Meta definition for RiskFolder."""

        verbose_name = 'Risk Folder'
        verbose_name_plural = 'Risk Folders'

    def to_risk(self) -> bool:
        """
        Determines whether the risk should be executed based on the strategy and value of the RiskFolder instance.
        If the strategy is 'amount', the function checks if the current value is equal to the value of the instance.
        If the strategy is 'percentage', the function generates a random number between 0 and 1 and checks if it is less than the value of the instance divided by 100.
        If the risk should be executed, the function resets the current value to 0 and returns True. Otherwise, it increments the current value by 1 and returns False.

        Returns:
            bool: True if the risk should be executed, False otherwise.
        """
        to_execute = False
        if self.strategy == self.StrategyChoices.AMOUNT:
            if self.is_full():
                self.current_value = 0
                to_execute = True
            else:
                self.current_value += 1
        elif self.strategy == self.StrategyChoices.PERCENTAGE:
            to_execute = random.random() < self.value / 100
        self.save()
        return to_execute

    def execute(self, trafficdata, **kwargs):
        print('executing risk')
        if self.to_risk():
            print('to risk')
            self.executed_risks.get_or_create(
                trafficdata=trafficdata)
            trafficdata.is_risky = True
            trafficdata.afm_state = kwargs.get('source')

    def empty(self):
        self.current_value = 0
        self.save()

    def is_full(self):
        return self.current_value == self.value

    def clean(self):
        super().clean()
        if self.strategy == self.StrategyChoices.PERCENTAGE and self.value > 100:
            raise ValidationError(
                {'value': 'Percentage cannot be greater than 100'})
        if self.strategy == self.StrategyChoices.AMOUNT and self.current_value > self.value:
            raise ValidationError(
                {'current_value': 'Current value cannot be greater than value'})

    def save(self, *args, **kwargs):
        if self.strategy == self.StrategyChoices.PERCENTAGE:
            self.current_value = 0

        self.clean()
        super().save(*args, **kwargs)

    def pass_rule(self, **kwargs):
        return self.state == kwargs.get('target')

    def __str__(self):
        return f'{self.current_value} / {self.value}' if self.strategy == 'amount' else f'{self.value}%'


class ExecutedRisk(models.Model):
    RISK, RELEASED = 'risk', 'released'
    STATUS_CHOICES = ((RISK, 'Risk'), (RELEASED, 'Released'))
    trafficdata = models.OneToOneField(
        'trafficdata.TrafficData', on_delete=models.CASCADE, related_name='executed_risk')

    risk_folder = models.ForeignKey(
        'RiskFolder', related_name='executed_risks', null=True, on_delete=models.SET_NULL)

    status = models.CharField(
        max_length=255, choices=STATUS_CHOICES, default=RISK)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta definition for ExecutedRisk."""

        verbose_name = 'Executed Risk'
        verbose_name_plural = 'Executed Risks'

    @ property
    def affiliate(self):
        return self.lead.affiliate

    def get_state(self):
        return self.trafficdata.get_state()

    def get_state_display(self):
        return self.trafficdata.get_state_display()

    @ property
    def country(self):
        return self.trafficdata.country

    @ property
    def trafficdata_id(self):
        return self.trafficdata.id

    def __str__(self):
        return f'{self.trafficdata} - {self.status}'


class SMSManagementQuerySet(PolymorphicMPTTQuerySet):
    ...


class SMSManagement(Folder, Management):
    objects = SMSManagementQuerySet.as_manager()

    class Meta:
        """Meta definition for SMSManagement."""
        verbose_name = 'SMS Management'
        verbose_name_plural = 'SMS Managements'


class SMSAdvertiserFolder(SMSManagement, AdvertiserFolder):
    ...


class SMSAffiliateFolder(SMSManagement, AffiliateFolder):
    ...


class SMSCountryFolder(SMSManagement, CountryFolder):
    ...


class SMSFolder(TargetFolder, SMSManagement):
    message = models.TextField()
    state = models.CharField(
        max_length=255, choices=TargetFolder.StateChoices.choices, default=TargetFolder.StateChoices.CLICK)

    can_have_children = False
    can_be_root = False

    @ property
    def icon(self):
        return 'https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/S.svg'

    @ property
    def neutrino(self) -> Neutrino:
        return CRMSettings.neutrino()

    def render(self, context):
        template = Template(self.message)
        return template.render(Context(context))

    def execute(self, lead, **kwargs):
        serialized_lead = lead.get_serialized_data()
        # will need to change this to retrieve the phone number from the lead
        phone_number = str(lead.phone)
        message = self.render(serialized_lead)
        lead.info(f'Sending SMS to {lead.phone} with message {message}')
        response = self.neutrino.send_sms(phone_number, message)
        return response

    def clean(self):
        if not self.neutrino:
            raise SMSFolderException('Neutrino is not configured')

    def pass_rule(self, **kwargs):
        return self.state == kwargs.get('target')

    class Meta:
        """Meta definition for SMSFolder."""

        verbose_name = 'SMS Folder'
        verbose_name_plural = 'SMS Folders'


class QueueManagementManager(models.Manager):
    def get_queue(self, country):
        try:
            return self.get(country=country, is_enabled=True)
        except QueueManagement.DoesNotExist:
            raise QueueManagement.QueueManagementException(
                f'Queue for {country} does not exist')


class QueueManagement(models.Model):
    class QueueManagementException(ValidationError):
        ...

    class DayChoices(models.IntegerChoices):
        MONDAY = 0, _('Monday')
        TUESDAY = 1, _('Tuesday')
        WEDNESDAY = 2, _('Wednesday')
        THURSDAY = 3, _('Thursday')
        FRIDAY = 4, _('Friday')
        SATURDAY = 5, _('Saturday')
        SUNDAY = 6, _('Sunday')

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

    # counter
    # counter = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Queue Management'
        verbose_name_plural = 'Queue Management'

    def __str__(self):
        return f'{self.country} - {self.from_hour} - {self.to_hour} - {self.from_day} - {self.to_day}'

    def clean(self):
        if self.from_hour >= self.to_hour:
            raise self.QueueManagementException(
                'from_hour must be less than to_hour')

    def should_get_in_queue(self) -> bool:
        """
        Check if the queue is enabled and if the lead should be filtered
        return true if the lead should get in the queue
        """
        return self.is_enabled and self.filter_rate > random.randint(0, 100)

    def get_thank_you_url(self):
        return self.thank_you_url

    def revoke(self, *args, **kwargs):
        return self.leads.filter(**kwargs).revoke()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def in_queue(self, day: datetime = None):
        if day is None:
            return self.leads.filter(status=QueueLeadStatusChoices.PENDING)

        # calculate the num of leads in the queue for the given day
        return self.leads.filter(status=QueueLeadStatusChoices.PENDING, time__date=day)

    def is_within_working_hours(self):
        # Get the current time in the current timezone
        current_time = datetime.now().time()
        current_day = datetime.now().weekday()  # Monday is 0 and Sunday is 6

        if self.from_day <= self.to_day:
            is_day_within = self.from_day <= current_day <= self.to_day
        else:
            # If the working days wrap around the end of the week (e.g., Sunday to Wednesday)
            is_day_within = self.from_day <= current_day or current_day <= self.to_day

        if self.from_hour <= self.to_hour:
            is_time_within = self.from_hour <= current_time <= self.to_hour
        else:
            # If the working hours wrap around midnight (e.g., 22:00 to 02:00)
            is_time_within = self.from_hour <= current_time or current_time <= self.to_hour

        return is_day_within and is_time_within

    def get_lead_send_time(self):
        current_time = timezone.now()

        last_lead = self.in_queue().order_by('-time').first()

        if last_lead:
            next_time = last_lead.time + timedelta(minutes=self.interval)
        else:
            next_time = current_time + timedelta(minutes=self.interval)

        next_day = next_time.weekday()

        if next_time.time() > self.to_hour or next_day < self.from_day or next_day > self.to_day:
            # Find the next working day
            if next_day >= self.to_day:
                days_until_next = 7 - next_day + self.from_day
            else:
                days_until_next = self.from_day - next_day

            # Calculate the date of the next working day
            send_date = (next_time + timedelta(days=days_until_next)).date()

            next_time = timezone.make_aware(
                datetime.combine(send_date, self.from_hour))

        return next_time

    def next_working_hour(self, now=timezone.now()) -> datetime:
        current_weekday = now.weekday()
        current_time = now.time()

        if self.from_day <= current_weekday <= self.to_day:
            if self.from_hour <= current_time < self.to_hour:
                next_working_hour = now  # Current time is within working hours
            elif current_time < self.from_hour:
                next_working_hour = datetime.combine(
                    now.date(), self.from_hour)  # It's before working hours today
            else:
                # It's after working hours today, go to the next working day
                if current_weekday == self.to_day:
                    # It's the last working day of the week, go to the start of working days next week
                    days_to_next = 7 - current_weekday + self.from_day
                else:
                    # It's not the last working day of the week, go to the next working day
                    days_to_next = 1
                next_working_hour = datetime.combine(
                    now.date() + timedelta(days=days_to_next), self.from_hour)
        elif current_weekday < self.from_day:
            # It's before the working days in the week
            days_to_next = self.from_day - current_weekday
            next_working_hour = datetime.combine(
                now.date() + timedelta(days=days_to_next), self.from_hour)
        else:  # current_weekday > self.to_day
            # It's after the working days in the week, go to the start of working days next week
            days_to_next = 7 - current_weekday + self.from_day
            next_working_hour = datetime.combine(
                now.date() + timedelta(days=days_to_next), self.from_hour)

        leads_in_queue = self.in_queue(next_working_hour.date()).count()
        # add interval minutes for each lead in the queue
        interval_in_seconds = random.randint(
            self.min_interval * 60, self.max_interval * 60)
        next_working_hour += timedelta(
            seconds=interval_in_seconds * leads_in_queue)

        # return the next working hour in the current timezone
        return timezone.make_aware(next_working_hour)


class Domain(models.Model):
    class DomainType(models.TextChoices):
        TRACKING, DASHBOARD = 'tracking', 'dashboard'

    domain = models.CharField(max_length=255, unique=True)
    redirect = models.BooleanField(default=True, verbose_name='Redirect to HTTPS',
                                   help_text='If checked, all HTTP requests will be redirected to HTTPS')
    created_at = models.DateTimeField(auto_now_add=True)
    affiliate = models.ForeignKey(
        'affiliate.Affiliate', on_delete=models.CASCADE, related_name='domains')

    type = models.CharField(
        max_length=255, choices=DomainType.choices, default=DomainType.TRACKING)

    is_verified = models.BooleanField('Verified', default=False)

    class Meta:
        verbose_name = 'Domain'
        verbose_name_plural = 'Domains'

    def __str__(self):
        return self.domain

    def save(self, *args, **kwargs):
        is_new_domain = self.pk is None
        super().save(*args, **kwargs)
        if is_new_domain:
            TXTRecord.objects.create(domain=self)


class TXTRecord(models.Model):
    domain = models.OneToOneField(
        'Domain', on_delete=models.CASCADE, related_name='txt_record')
    verification_code = models.CharField(
        max_length=255, help_text='Point domain TXT record to this value')

    class Meta:
        verbose_name = 'TXT Record'
        verbose_name_plural = 'TXT Records'

    def __str__(self):
        return f'TXT Record for {self.domain}'

    def generate_verification_code(self):
        timestamp = int(datetime.now().timestamp())
        domain_name = self.domain
        secret_key = settings.SECRET_KEY
        message = f'{domain_name}-{timestamp}-{secret_key}'.encode('utf-8')
        verification_code = hashlib.sha256(
            message).hexdigest()  # Generates a SHA-256 hash
        return verification_code

    def verify_code(self):
        try:
            answers = dns.resolver.resolve(self.domain.domain, 'TXT')
            for rdata in answers:
                for txt_string in rdata.strings:
                    if txt_string.decode('utf-8') == self.verification_code:
                        self.domain.is_verified = True
                        self.domain.save()
                        return True
            return False
        except dns.exception.DNSException:
            return False

    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = self.generate_verification_code()
        super().save(*args, **kwargs)


class EventData(models.Model):
    event = models.ForeignKey(
        'Event', on_delete=models.CASCADE, related_name='event_data')
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Event Data'
        verbose_name_plural = 'Event Data'


class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_unique = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    """
    event creation will be
    """

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-created_at']

    def count(self):
        return self.event_logs.count()

    def create_event(self, trafficdata_id):
        event_log = EventLog.objects.create_event_log(self, trafficdata_id)
        return event_log


class EventLogManager(models.Manager):
    def create_event_log(self, event, trafficdata):
        if isinstance(event, str):
            event_name = event
            event = Event.objects.get(name=event_name)

        if isinstance(trafficdata, int) or isinstance(trafficdata, str):
            from apps.trafficdata.models import TrafficData
            trafficdata_id = trafficdata
            trafficdata = TrafficData.objects.get(id=trafficdata_id)

        is_unique = event.is_unique
        if is_unique:
            event_logs = EventLog.objects.filter(
                event=event, trafficdata=trafficdata)
            if event_logs.exists():
                return event_logs.first()

        event_log = EventLog.objects.create(
            event=event, trafficdata=trafficdata)
        return event_log


class EventLog(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='event_logs')
    trafficdata = models.ForeignKey(
        'trafficdata.TrafficData', on_delete=models.CASCADE, related_name='event_logs')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = EventLogManager()

    def __str__(self):
        return f'{self.event.name} - {self.trafficdata}'

    class Meta:
        verbose_name = 'Event Log'
        verbose_name_plural = 'Event Logs'
        ordering = ['-created_at']
