import jwt
import requests
from django.conf import settings
from django_countries.fields import CountryField
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template import Context, Template
from django.utils import timezone
from django_fsm.signals import post_transition

from apps.telegrambot.views import Telegram
from apps.trafficdata.states import StateChoices, PostbackStatusChoices
from apps.utils.facebook import FacebookConversionAPI
from apps.utils.models import LogModelMixin
from apps.users.models import User

from .managers import AffiliateQuerySet, EventNotificationQuerySet, PostbackQuerySet, TelegramProfileQuerySet
from .tasks import schedule_fire


class IPWhitelist(models.Model):
    ip_address = models.GenericIPAddressField(verbose_name='IP Address')
    api_token = models.ForeignKey(
        'APIToken', on_delete=models.CASCADE, related_name='ip_whitelist')

    class Meta:
        verbose_name = 'IP'
        verbose_name_plural = 'IP Addresses'

    def __str__(self):
        return ''


class APIToken(models.Model):
    class DuplicationStrategyChoices(models.TextChoices):
        DISABLE, GLOBAL_WEEK_WINDOW, CURRENT_TOKEN_WEEK_WINDOW = 'disable', 'global_week_window', 'current_token_week_window'

    class DuplicationFieldChoices(models.TextChoices):
        DISABLE, EMAIL, PHONE_NUMBER, IP_ADDRESS = 'disable', 'email', 'phone_number', 'ip_address'

    affiliate = models.ForeignKey(
        'Affiliate', on_delete=models.CASCADE, related_name='api_tokens', editable=False,)

    is_active = models.BooleanField(default=True, verbose_name='Enabled')

    can_see_real_status = models.BooleanField(
        default=False, verbose_name='Can see real status', help_text='Whether this affiliate can see real status of leads')

    can_see_lead_info = models.BooleanField(
        default=False, verbose_name='Can see lead info', help_text='Whether this affiliate can see lead info')

    token = models.CharField(max_length=255, unique=True, verbose_name='Token',
                             help_text='Token to be used in API requests')

    duplication_strategy = models.CharField(max_length=255, choices=DuplicationStrategyChoices.choices, default='disable', verbose_name='Duplication Strategy',
                                            help_text='Duplication strategy to be used in API requests')

    duplication_field = models.CharField(max_length=255, choices=DuplicationFieldChoices.choices, default='email', verbose_name='Duplication Field',
                                         help_text='Duplication field to be used in API requests')

    phone_validation = models.BooleanField(
        default=False, verbose_name='Phone Validation', help_text='Whether to validate the lead\'s phone number')

    email_validation = models.BooleanField(
        default=False, verbose_name='Email Validation', help_text='Whether to validate the lead\'s email')

    offer = models.ForeignKey('offer.Offer', on_delete=models.CASCADE,
                              related_name='api_tokens', verbose_name='Offer')

    class Meta:
        verbose_name = 'API Token'
        verbose_name_plural = 'API Tokens'

    @receiver(pre_save)
    def generate_token(sender, instance, *args, **kwargs):
        if sender == APIToken and not instance.token:
            instance.token = jwt.encode(
                {
                    'id': instance.affiliate.id,
                    'c': timezone.now().timestamp()
                }, key=settings.SECRET_KEY, algorithm='HS256')

    def ip_exists(self, ip_address):
        return self.ip_whitelist.filter(ip_address=ip_address).exists()

    def decode(self):
        return jwt.decode(self.token, key=settings.SECRET_KEY, algorithms=['HS256'])

    def __str__(self):
        return self.token


class Affiliate(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='affiliate')
    company_name = models.CharField(max_length=30)
    country = CountryField()
    telegram = models.CharField(max_length=30)
    skype = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True, verbose_name='Status')

    date_joined = None

    objects = AffiliateQuerySet.as_manager()

    class Meta:
        verbose_name = 'Affiliate'
        verbose_name_plural = 'Affiliates'

    def __str__(self):
        return self.company_name

    @property
    def username(self):
        return self.email

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def email(self):
        return self.user.email

    # @property
    # def is_active(self):
    #     return self.user.is_active

    class Meta:
        """Meta definition for Affiliate."""

        verbose_name = 'Affiliate'
        verbose_name_plural = 'Affiliates'

    def disable(self):
        self.is_active = False
        self.save()
        return self

    def enable(self):
        self.is_active = True
        self.save()
        return self

    def ip_exists(self, ip):
        return self.api_tokens.filter(ip_whitelist__ip_address=ip).exists()

    def clicks(self):
        return self.trafficdata.clicks()

    def leads(self):
        return self.trafficdata.leads()

    def sales(self):
        return self.trafficdata.sales()

    def __str__(self):
        return self.company_name

    def get_pixels(self, **kwargs):
        return self.pixels.filter(active=True, **kwargs)

    def get_chat_id(self):
        if self.telegram_profile.chat_id:
            return self.telegram_profile.chat_id

    def notify_telegram(self, state, **kwargs):
        if hasattr(self, 'telegram_profile'):
            self.telegram_profile.notify(state, **kwargs)


class Postback(LogModelMixin):
    class MethodChoices(models.TextChoices):
        GET, POST = ('GET', 'GET'), ('POST', 'POST')

    objects = PostbackQuerySet.as_manager()

    affiliate = models.ForeignKey(
        Affiliate, on_delete=models.CASCADE, related_name='postbacks')
    method = models.CharField(
        max_length=4, choices=MethodChoices.choices, default=MethodChoices.GET)
    content = models.CharField(max_length=255)
    goal = models.CharField(
        max_length=20, choices=StateChoices.choices, default=StateChoices.LEAD_PUSHED)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Postback'
        verbose_name_plural = 'Postbacks'

    def __str__(self):
        return self.affiliate.company_name

    def fire(self, lead):
        content = self.content
        method = self.method
        schedule_fire.apply_async((lead.id, content, method), countdown=1)

    def pending(self, postback, lead):
        lead.executed_postbacks.create(
            status=PostbackStatusChoices.PENDING,
            content=postback.content,
            method=postback.method,
            trafficdata=lead,
        )


class Pixel(LogModelMixin):
    class PixelTypeChoices(models.TextChoices):
        BODY_HTML_INSERT, SCRIPT_EVALUATE, INLINE_IFRAME_URL, INLINE_SCRIPT_URL, INLINE_SCRIPT_IMG = 'body_html_insert', 'script_evaluate', 'inline_iframe_url', 'inline_script_url', 'inline_script_img'

    affiliate = models.ForeignKey(
        Affiliate, on_delete=models.CASCADE, related_name='pixels')
    content = models.TextField()
    goal = models.CharField(
        max_length=20, choices=StateChoices.choices, default=StateChoices.LEAD_PUSHED)
    type = models.CharField(max_length=30, choices=PixelTypeChoices.choices,
                            default=PixelTypeChoices.BODY_HTML_INSERT, verbose_name='Pixel Type')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pixel'
        verbose_name_plural = 'Pixels'

    def __str__(self):
        return self.affiliate.company_name


class AffiliateRequestLog(models.Model):
    request_method = models.CharField(max_length=50)
    request_url = models.CharField(max_length=255)
    request_referrer = models.CharField(max_length=255, null=True, blank=True)
    request_headers = models.TextField(null=True, blank=True)
    lead = models.ForeignKey('trafficdata.TrafficData',
                             on_delete=models.CASCADE, related_name='affiliate_request_logs', null=True, blank=True)
    request_input = models.TextField()
    token = models.ForeignKey(
        APIToken, on_delete=models.CASCADE, related_name='request_logs')
    response = models.TextField()
    code = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Affiliate Request Log'
        verbose_name_plural = 'Affiliate Request Logs'

    @property
    def affiliate(self):
        return self.token.affiliate


class TelegramProfile(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = Telegram()

    affiliate = models.OneToOneField(
        Affiliate, on_delete=models.CASCADE, related_name='telegram_profile')
    chat_id = models.CharField(max_length=50, blank=True, null=True)

    objects = TelegramProfileQuerySet.as_manager()

    def __str__(self):
        return f'{self.chat_id}'

    def notify(self, state, **kwargs):
        self.event_notifications.notify(state, **kwargs)


class EventNotification(models.Model):
    objects = EventNotificationQuerySet.as_manager()
    state = models.CharField(
        max_length=20, choices=StateChoices.choices, default=StateChoices.LEAD_PUSHED)
    message = models.TextField()
    telegram_profile = models.ForeignKey(
        TelegramProfile, on_delete=models.CASCADE, related_name='event_notifications')
    topic = models.CharField(max_length=255,)

    def __str__(self):
        return self.state

    def render_message(self, kwargs):
        template = Template(self.message)
        return template.render(Context(kwargs))

    def notify(self, **kwargs):
        message = self.render_message(kwargs)

        tread_id = self.topic
        self.telegram_profile.bot.send_message(
            self.telegram_profile.chat_id, message, reply_to_message_id=tread_id, parse_mode='Markdown')


class Proxy(models.Model):
    class ProtocolChoices(models.TextChoices):
        HTTP = 'http'
        HTTPS = 'https'
        SOCKS5 = 'socks5'

    protocol = models.CharField(
        max_length=6, choices=ProtocolChoices.choices, default=ProtocolChoices.HTTP)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Proxy'
        verbose_name_plural = 'Proxies'

    def __str__(self):
        return self.get_proxy()

    def get_proxy(self):
        return f'{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}'

    def check_proxy(self):
        try:

            proxies = {
                'http': self.get_proxy(),
                'https': self.get_proxy()
            }
            r = requests.get('https://example.com/', proxies=proxies,
                             timeout=10, headers={'User-Agent': self.user_agent})
            return r.ok
        except:
            return False


class FacebookPixel(models.Model):
    class FacebookEventChoices(models.TextChoices):
        ADD_PAYMENT_INFO = 'AddPaymentInfo'
        ADD_TO_CART = 'AddToCart'
        ADD_TO_WISHLIST = 'AddToWishlist'
        COMPLETE_REGISTRATION = 'CompleteRegistration'
        CONTACT = 'Contact'
        CUSTOMIZE_PRODUCT = 'CustomizeProduct'
        DONATE = 'Donate'
        FIND_LOCATION = 'FindLocation'
        INITIATE_CHECKOUT = 'InitiateCheckout'
        LEAD = 'Lead'
        PAGE_VIEW = 'PageView'
        PURCHASE = 'Purchase'
        SCHEDULE = 'Schedule'
        SEARCH = 'Search'
        START_TRIAL = 'StartTrial'
        SUBMIT_APPLICATION = 'SubmitApplication'
        SUBSCRIBE = 'Subscribe'
        VIEW_CONTENT = 'ViewContent'

    name = models.CharField(max_length=255)

    affiliate = models.ForeignKey(
        Affiliate, on_delete=models.CASCADE, related_name='facebook_pixels')
    pixel_id = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    proxy = models.OneToOneField(
        Proxy, on_delete=models.CASCADE, related_name='facebook_pixel', null=True, blank=True)

    goal = models.CharField(
        max_length=255, choices=StateChoices.choices, default=StateChoices.LEAD)

    event_name = models.CharField(
        max_length=255, choices=FacebookEventChoices.choices, default=FacebookEventChoices.ADD_PAYMENT_INFO)

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Facebook Pixel'
        verbose_name_plural = 'Facebook Pixels'

    def __str__(self):
        return self.pixel_id

    def fire(self, context=None):
        fb_api = FacebookConversionAPI(
            access_token=self.access_token, pixel_id=self.pixel_id, proxy=self.proxy)
        return fb_api.sendEvent(event_name=self.event_name)
