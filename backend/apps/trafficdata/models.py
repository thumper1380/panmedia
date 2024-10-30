from polymorphic.models import PolymorphicModel
from datetime import timedelta
from .managers import TrafficDataQuerySet, ConversionQuerySet
import calendar
import hashlib
import jwt
import pytz
import time
from datetime import datetime, timedelta
from config.celery import app
from django.conf import settings
from django.core.cache import cache

from django.db import models
from django.urls import reverse
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_description
from django_countries.fields import CountryField
from djmoney.models.fields import MoneyField, Money

from apps.leads_conversions.models import Payouts, Revenues
from apps.settings.models import CRMSettings, QueueManagement
from apps.traffic_distribution.models import (CapFolderQuerySet,
                                              RotationControl)

from apps.settings.models import Source

from .states import (PostbackMethodChoices, PostbackStatusChoices,
                     StateChoices, QueueLeadStatusChoices,
                     TrafficDataLogTypeChoices,
                     TrafficDataLogTypeColors
                     )
from .tasks import fire_executed_postback
from .managers import (
    QueueLeadQuerySet, ExecutedPostbackQuerySet,
    ClickManager, LeadManager, SaleManager, AffiliateClickManager, AffiliateLeadManager, AffiliateSaleManager,
)

from .defaults import DEFAULT_PUSH_STATUS

from apps.utils.models import LogModel, LogModelMixin
from apps.traffic_distribution.models import RotationControl
from apps.traffic_distribution.models import CapFolderQuerySet
from apps.traffic_distribution.exceptions import RotationDoesNotExist, AdvertiserRejectedException
from .exceptions import PushLeadException
from django.utils import timezone


from .decorators import logged_transition


class TimeRange:
    TODAY, YESTERDAY, THIS_WEEK, LAST_WEEK, THIS_MONTH, LAST_MONTH, THIS_YEAR, LAST_YEAR, ALL_TIME = 'today', 'yesterday', 'this_week', 'last_week', 'this_month', 'last_month', 'this_year', 'last_year', 'all_time'

    VS_TIME_RANGE = {
        TODAY: YESTERDAY,
        THIS_WEEK: LAST_WEEK,
        THIS_MONTH: LAST_MONTH,
        THIS_YEAR: LAST_YEAR,
    }

    def __init__(self, interval: str):
        self.interval = interval.lower().replace(' ', '_')

    def get_vs_time_range(self):
        return self.VS_TIME_RANGE.get(self.interval, self.ALL_TIME)

    def get_time_zone(self):
        time_zone = CRMSettings.objects.time_zone()
        tz = pytz.timezone(time_zone)
        return tz

    def now(self):
        return datetime.now(self.get_time_zone())

    def calc(self):
        """
        calc time range base on interval and time zone
        interval could be one of the following:
        - today
        - yesterday
        - this_week
        - last_week
        - this_month
        - last_month
        - this_year
        - last_year
        - all_time
        """
        now = datetime.now()

        if self.interval == self.TODAY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=23, minute=59,
                              second=59, microsecond=999999)
        elif self.interval == self.YESTERDAY:
            yesterday = now - timedelta(days=1)
            start = yesterday.replace(
                hour=0, minute=0, second=0, microsecond=0)
            end = yesterday.replace(
                hour=23, minute=59, second=59, microsecond=999999)
        elif self.interval == self.THIS_WEEK:
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=23, minute=59,
                              second=59, microsecond=999999)
        elif self.interval == self.LAST_WEEK:
            start = now - timedelta(days=now.weekday() + 7)
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=6)
            end = end.replace(hour=23, minute=59,
                              second=59, microsecond=999999)
        elif self.interval == self.THIS_MONTH:
            start = now.replace(day=1, hour=0, minute=0,
                                second=0, microsecond=0)
            end = now.replace(hour=23, minute=59,
                              second=59, microsecond=999999)
        elif self.interval == self.LAST_MONTH:
            start = now.replace(day=1, hour=0, minute=0,
                                second=0, microsecond=0) - timedelta(days=1)
            end = start.replace(day=calendar.monthrange(start.year, start.month)[
                                1], hour=23, minute=59, second=59, microsecond=999999)
        elif self.interval == self.THIS_YEAR:
            start = now.replace(month=1, day=1, hour=0,
                                minute=0, second=0, microsecond=0)
            end = now.replace(hour=23, minute=59,
                              second=59, microsecond=999999)
        elif self.interval == self.LAST_YEAR:
            start = now.replace(month=1, day=1, hour=0, minute=0,
                                second=0, microsecond=0) - timedelta(days=1)
            end = start.replace(year=start.year + 1, month=1, day=1, hour=0,
                                minute=0, second=0, microsecond=0) - timedelta(days=1)
        elif self.interval == self.ALL_TIME:
            start = datetime.min
            end = datetime.max
        else:
            raise ValueError('Invalid interval')
        return start, end


class QueueLead(LogModelMixin):
    trafficdata = models.OneToOneField(
        'TrafficData', on_delete=models.CASCADE, related_name='queue')
    objects = QueueLeadQuerySet.as_manager()
    status = models.CharField(
        max_length=10, choices=QueueLeadStatusChoices.choices, default=QueueLeadStatusChoices.PENDING)
    time = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    queue = models.ForeignKey(
        QueueManagement, on_delete=models.CASCADE, related_name='leads')

    task_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Lead'
        verbose_name_plural = 'Queue'

    def __str__(self):
        return f'{self.id} - {self.status}'

    def revoke(self):
        if not self.task_id:
            return
        app.control.revoke(self.task_id)
        self.status = QueueLeadStatusChoices.REVOKED
        self.time = None
        self.save()
        return True

    def set_status(self, status):
        self.status = status
        self.save()


class AdvertiserSaleStatus(models.Model):
    trafficdata = models.ForeignKey(
        'TrafficData', on_delete=models.CASCADE, related_name='advertiser_sale_statuses')
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.status}'

    class Meta:
        verbose_name_plural = 'Advertiser Sale Statuses'

    def save(self, *args, **kwargs):
        if not self.trafficdata.is_risky:
            # self.trafficdata.afm_status = self.status # bug fix
            # self.trafficdata.save()
            ...
        super().save(*args, **kwargs)


class ExecutedPostback(models.Model):
    objects = ExecutedPostbackQuerySet.as_manager()
    task_id = models.CharField(
        'Task ID', max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=PostbackStatusChoices.choices)
    trafficdata = models.ForeignKey(
        'TrafficData', on_delete=models.CASCADE, related_name='executed_postbacks')
    content = models.CharField(max_length=255)
    method = models.CharField(
        max_length=10, choices=PostbackMethodChoices.choices)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.trafficdata} - {self.status}'

    class Meta:
        verbose_name = 'Executed Postback'
        verbose_name_plural = 'Executed Postbacks'

    def revoke(self):
        if self.task_id:
            app.control.revoke(self.task_id)
            self.status = PostbackStatusChoices.REVOKED
            self.save()
            return True
        return False

    def fire(self):
        fire_executed_postback.delay(self.id)


class AutoLogin(models.Model):
    url = models.CharField(max_length=500)
    ip_address = models.CharField(max_length=30)
    proxy_passed = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.trafficdata} - {self.url}'

    class Meta:
        verbose_name = 'Auto Login'
        verbose_name_plural = 'Auto Logins'

    def redirect_url(self):
        jwt_token = jwt.encode(
            {
                'i': self.trafficdata.id,
                's': self.trafficdata.secret,
                't': int(time.time()),
                'ip_address': self.ip_address,
            },
            settings.SECRET_KEY, algorithm='HS256'
        )
        redirect_url = '/api/redirect'

        REDIRECT_URL_PARAMETER_NAME = settings.REDIRECT_URL_PARAMETER_NAME

        return f'{redirect_url}?{REDIRECT_URL_PARAMETER_NAME}={jwt_token}'

    def _pass(self, ip_address):
        self.proxy_passed = True
        self.created_at = timezone.now()
        self.ip_address = ip_address
        self.save()

    @property
    def is_authentic(self) -> bool:
        # return self.ip_address == self.trafficdata.ip_address if self.proxy_passed else None
        return '172.18.0.8' == self.trafficdata.ip_address


# import polymorphic


class TrafficDataLog(PolymorphicModel):
    trafficdata = models.ForeignKey(
        'TrafficData', on_delete=models.CASCADE, related_name='logs')
    color = models.CharField(
        max_length=20, choices=TrafficDataLogTypeColors.choices, default=TrafficDataLogTypeColors.GREEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log'
        verbose_name_plural = 'Logs'

    def __str__(self):
        return ''


class StateSwitchedLog(TrafficDataLog):
    source_state = models.CharField(
        max_length=20, choices=StateChoices.choices, default=None)
    target_state = models.CharField(
        max_length=20, choices=StateChoices.choices, default=None)

    def save(self, *args, **kwargs):
        self.color = TrafficDataLogTypeColors.BLUE
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'State Switched'


class StateInitiatedLog(TrafficDataLog):
    initial_state = models.CharField(
        max_length=20, choices=StateChoices.choices, default=None)

    def save(self, *args, **kwargs):
        self.color = TrafficDataLogTypeColors.GREEN
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'State Initiated'


class PushingErrorLog(TrafficDataLog):
    message = models.TextField()

    def save(self, *args, **kwargs):
        self.color = TrafficDataLogTypeColors.RED
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Pushing Error'


class PushingAttemptLog(TrafficDataLog):
    message = models.TextField()

    def save(self, *args, **kwargs):
        self.color = TrafficDataLogTypeColors.YELLOW
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Pushing Attempt'


class TrafficData(models.Model, LogModel):
    class Meta:
        verbose_name = 'Traffic Data'
        verbose_name_plural = 'Traffic Data'

    objects = TrafficDataQuerySet.as_manager()
    state = FSMField(default=None, choices=StateChoices.choices,
                     blank=True, null=True, max_length=20, protected=True)

    profile = models.JSONField(default=dict, blank=True, null=True)

    country = CountryField(verbose_name='Country')
    region = models.CharField(blank=True, max_length=30)
    city = models.CharField(blank=True, max_length=30)
    language = models.CharField(blank=True, max_length=30, null=True)

    afm_state = models.CharField(
        default=None, choices=StateChoices.choices, blank=True, null=True, max_length=20)

    afm_status = models.CharField(
        max_length=20, blank=True, null=True, default=None)

    affiliate = models.ForeignKey(
        'affiliate.Affiliate', on_delete=models.CASCADE, related_name='trafficdata', verbose_name='Affiliate',)

    funnel = models.ForeignKey(
        'offer.Offer', on_delete=models.CASCADE, related_name='trafficdata')

    advertiser_external_id = models.CharField(
        'Advertiser External ID', max_length=100, blank=True, null=True)

    advertiser = models.ForeignKey(
        'traffic_distribution.Advertiser', on_delete=models.CASCADE, blank=True, null=True, related_name='trafficdata', verbose_name='Advertiser')

    auto_login = models.OneToOneField(
        AutoLogin, on_delete=models.CASCADE, blank=True, null=True, related_name='trafficdata')

    thank_you_url = models.CharField(
        'Thank You URL', max_length=500, blank=True, null=True)

    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, blank=True, null=True, related_name='trafficdata', verbose_name='Source')

    # Affiliate Subs
    aff_sub_1 = models.CharField(
        verbose_name="Aff Sub 1", blank=True, max_length=100)
    aff_sub_2 = models.CharField(
        verbose_name="Aff Sub 2", blank=True, max_length=100)
    aff_sub_3 = models.CharField(
        verbose_name="Aff Sub 3", blank=True, max_length=100)
    aff_sub_4 = models.CharField(
        verbose_name="Aff Sub 4", blank=True, max_length=100)
    aff_sub_5 = models.CharField(
        verbose_name="Aff Sub 5", blank=True, max_length=100)
    aff_sub_6 = models.CharField(
        verbose_name="Aff Sub 6", blank=True, max_length=100)
    aff_sub_7 = models.CharField(
        verbose_name="Aff Sub 7", blank=True, max_length=100)
    aff_sub_8 = models.CharField(
        verbose_name="Aff Sub 8", blank=True, max_length=100)
    aff_sub_9 = models.CharField(
        verbose_name="Aff Sub 9", blank=True, max_length=100)
    aff_sub_10 = models.CharField(
        verbose_name="Aff Sub 10", blank=True, max_length=100)
    aff_sub_11 = models.CharField(
        verbose_name="Aff Sub 11", blank=True, max_length=100)
    aff_sub_12 = models.CharField(
        verbose_name="Aff Sub 12", blank=True, max_length=100)
    aff_sub_13 = models.CharField(
        verbose_name="Aff Sub 13", blank=True, max_length=100)
    aff_sub_14 = models.CharField(
        verbose_name="Aff Sub 14", blank=True, max_length=100)
    aff_sub_15 = models.CharField(
        verbose_name="Aff Sub 15", blank=True, max_length=100)
    aff_sub_16 = models.CharField(
        verbose_name="Aff Sub 16", blank=True, max_length=100)
    aff_sub_17 = models.CharField(
        verbose_name="Aff Sub 17", blank=True, max_length=100)
    aff_sub_18 = models.CharField(
        verbose_name="Aff Sub 18", blank=True, max_length=100)
    aff_sub_19 = models.CharField(
        verbose_name="Aff Sub 19", blank=True, max_length=100)
    aff_sub_20 = models.CharField(
        verbose_name="Aff Sub 20", blank=True, max_length=100)

    # Advertiser Subs
    adv_sub_1 = models.CharField(
        verbose_name="Adv Sub 1", blank=True, max_length=50)
    adv_sub_2 = models.CharField(
        verbose_name="Adv Sub 2", blank=True, max_length=50)
    adv_sub_3 = models.CharField(
        verbose_name="Adv Sub 3", blank=True, max_length=50)
    adv_sub_4 = models.CharField(
        verbose_name="Adv Sub 4", blank=True, max_length=50)
    adv_sub_5 = models.CharField(
        verbose_name="Adv Sub 5", blank=True, max_length=50)

    device_type = models.CharField(
        "Device Type", max_length=30, blank=True, null=True)
    user_agent = models.CharField(
        "User Agent", max_length=200, blank=True, null=True)
    os = models.CharField(verbose_name="OS", max_length=30, blank=True, null=True)
    os_version = models.CharField(
        "OS Version", max_length=30, blank=True, null=True)
    browser = models.CharField("Browser", max_length=30, blank=True, null=True)
    browser_version = models.CharField(
        'Browser Version', max_length=30, blank=True, null=True)
    device_model = models.CharField(
        "Device Model", max_length=30, blank=True, null=True)
    ip_address = models.CharField(
        verbose_name="IP Adress", blank=True, max_length=30)
    bot = models.BooleanField(default=False)
    connection_type = models.CharField(
        "Connection Type", max_length=30, blank=True)
    mobile_operator = models.CharField(
        'Mobile Operator', max_length=30, blank=True)
    x_requested_with = models.CharField(
        'X-Requested-With', max_length=30, blank=True, null=True)
    isp = models.CharField('ISP', max_length=30, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True)

    proxy = models.BooleanField(default=False)

    is_unique = models.BooleanField('Unique', default=None, null=True)

    retry_count = models.IntegerField('Retry Count', default=0)

    referrer = models.CharField(
        'Referrer', max_length=500, blank=True, null=True)

    score = models.DecimalField(
        'Score', max_digits=5, decimal_places=2, blank=True, null=True)

    click_created_at = models.DateTimeField(auto_now_add=True)
    click_landed_created_at = models.DateTimeField(blank=True, null=True)
    lead_created_at = models.DateTimeField(blank=True, null=True)
    lead_pushed_created_at = models.DateTimeField(blank=True, null=True)
    sale_created_at = models.DateTimeField(blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    is_risky = models.BooleanField(default=False, verbose_name='Risky')

    def _get_profile_fields(self):
        # return all self.profile keys
        return self.funnel.lead_form.fields.values_list('key', flat=True)

    def _set_profile(self, **profile):
        fields = self._get_profile_fields()
        self.profile = {k: v for k, v in profile.items() if k in fields}

    def _get_profile_required_fields(self):
        from apps.settings.models import ValidationRule
        # return all self.profile keys
        return self.funnel.lead_form.fields.filter(validation_rules__rule_type=ValidationRule.RuleTypes.REQUIRED).values_list('key', flat=True)

    def __getattr__(self, attr):
        try:
            # First, try to get the attribute in the usual way
            return super().__getattr__(attr)
        except AttributeError:
            # If it's not a normal attribute, it might be a field in the profile
            if self.profile is not None and attr in self.profile:
                return self.profile[attr]
            else:
                raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute '{attr}'")

    def __str__(self):
        return f'{self.id}'

    @property
    def advertiser_sale_status(self):
        forced_sale_status = self.conversions.all().sale_status()
        if forced_sale_status:
            return forced_sale_status.name
        advertiser_sale_statuses: AdvertiserSaleStatus = self.advertiser_sale_statuses.all(
        ).order_by('-created_at')
        if advertiser_sale_statuses.exists():
            return advertiser_sale_statuses.first().status

    @property
    def sale_status_changed_times(self):
        return self.advertiser_sale_statuses.count()

    def update_status(self, status: str):
        if status != self.advertiser_sale_status:
            self.advertiser_sale_statuses.create(status=status)
                
        if self.advertiser:
            self.advertiser.add_unassigned_status(status)

    def get_state(self):
        return self.state

    @ property
    def secret(self):
        return hashlib.shake_128((str(self.id)+str(self.click_created_at.timestamp())).encode()).hexdigest(8)

    def encode_for_track(self):
        return jwt.encode({'i': self.id, 's': self.secret, 't': int(self.created_at.timestamp())}, settings.SECRET_KEY, algorithm='HS256')

    @property
    def p(self):
        return jwt.encode({'i': self.id, 's': self.secret, 't': int(self.created_at.timestamp())}, settings.SECRET_KEY, algorithm='HS256')

    # def log(self, type, message, **kwargs):
    #     self.logs.create(type=type, description=message, **kwargs)

    @classmethod
    def create_click(cls, **kwargs):
        click = cls.objects.create(
            click_created_at=datetime.now(),
            **kwargs)
        click.register_impression()
        click.save()
        return click

    @fsm_log_description
    @logged_transition(field=state, source=None, target=StateChoices.CLICK)
    def register_impression(self, **kwargs):
        cache_key = f"click_{self.user_agent}_{self.ip_address}"
        if cache.get(cache_key):
            self.is_unique = False
        else:
            settings = CRMSettings.load()
            uniqueness_ttl = settings.uniqueness_ttl
            timeout = uniqueness_ttl * 60 * 60
            self.is_unique = True
            cache.set(cache_key, True, timeout=timeout)

    @fsm_log_description
    @logged_transition(field=state, source=[StateChoices.LEAD, StateChoices.LEAD_DECLINED], target=StateChoices.LEAD_QUEUED)
    def queue_lead(self, eta, queue, **kwargs):
        # eta = datetime.now() + timedelta(seconds=random.randint(1, 60)) # for testing purposes only

        QueueLead.objects.create(trafficdata=self, time=eta, queue=queue)

    @ fsm_log_description
    @ logged_transition(field=state, source=StateChoices.CLICK, target=StateChoices.CLICK_LANDED)
    def impression_registered(self):
        self.click_landed_created_at = datetime.now()

    @ fsm_log_description
    @ logged_transition(field=state, source=[None, StateChoices.LEAD_DECLINED, StateChoices.LEAD, StateChoices.CLICK_LANDED], target=StateChoices.LEAD)
    def form_complete(self, **kwargs):
        self.lead_created_at = datetime.now()

        # add description

    @ fsm_log_description
    @ logged_transition(field=state, source=[StateChoices.LEAD, StateChoices.LEAD_QUEUED], target=StateChoices.LEAD_PUSHED)
    def advertiser_accepted(self, advertiser_external_id, advertiser_id, auto_login_url, status=DEFAULT_PUSH_STATUS, **kwargs):
        self.advertiser_external_id = advertiser_external_id
        self.advertiser_id = advertiser_id

        autologin = AutoLogin.objects.create(
            url=auto_login_url)

        self.auto_login = autologin

        self.lead_pushed_created_at = datetime.now()

        self.update_status(status=status)

    @ fsm_log_description
    @ logged_transition(field=state, source=[StateChoices.LEAD, StateChoices.LEAD_QUEUED], target=StateChoices.LEAD_DECLINED)
    def advertisers_declined(self, **kwargs):
        pass

    @ fsm_log_description
    @ logged_transition(field=state, source=StateChoices.LEAD_DECLINED, target=StateChoices.LEAD)
    def try_again(self, **kwargs) -> 'function':
        pass

    @ fsm_log_description
    @ logged_transition(field=state, source=StateChoices.LEAD_PUSHED, target=StateChoices.SALE)
    def advertiser_ftd_event(self, **kwargs):
        self.sale_created_at = datetime.now()

    def get_form(self):
        return self.funnel.lead_form

    def set_auto_login_url(self, url):
        autologin = AutoLogin.objects.create(
            url=url)

        self.auto_login = autologin

        self.save()

    def release_risk(self):
        if self.is_risky:
            self.is_risky = False
            self.afm_status = self.advertiser_sale_status
            self.afm_state = self.state
            self.save()
            # TODO: fire postbacks
            self.executed_postbacks.fire()

    def generate_auto_login_url(self):
        if self.auto_login:
            return self.auto_login.redirect_url()
        else:
            return self.thank_you_url

    @ property
    def sale_statuses(self):
        return self.advertiser.get_sale_statuses()

    def get_payout(self) -> Money:
        funnel_payout = self.funnel.cpa
        payout = Payouts.objects.tree(**self.get_serialized_data())
        return funnel_payout if funnel_payout else payout.value if payout else Money(0, 'USD')

    def get_revenue(self) -> Money:
        funnel_revenue = self.funnel.revenue
        revenue = Revenues.objects.tree(**self.get_serialized_data())
        return funnel_revenue if funnel_revenue else revenue.value if revenue else Money(0, 'USD')

    def push_brands(self, raise_exception=True) -> bool:
        try:
            queue_management: QueueManagement = QueueManagement.objects.get_queue(
                country=self.country)

            if queue_management.should_get_in_queue() and not queue_management.is_within_working_hours():
                message = f'Lead {self.id} added to queue #{queue_management.id}'
                self.queue_lead(
                    description=message,
                    eta=queue_management.next_working_hour(),
                    queue=queue_management
                )
                thank_you_url = queue_management.get_thank_you_url()
                self.set_auto_login_url(thank_you_url)
                self.save()
                return True
        except QueueManagement.DoesNotExist:
            pass
        except QueueManagement.QueueManagementException:
            pass
        except Exception as e:
            self.error(f'Queue management error: {e}')
            if raise_exception:
                raise e

        caps: CapFolderQuerySet = RotationControl.search(
            affiliate_id=self.affiliate.id, country=self.country)
        if not caps.exists():
            self.debug(
                f'Rotation does not exist: There is no active rotation for this affiliate {self.affiliate.company_name} / #{self.affiliate.id}')
            self.advertisers_declined(
                description=f'There is no active rotation for this affiliate {self.affiliate.company_name} / #{self.affiliate.id}')
            self.save()
            raise PushLeadException(
                f'There is no active rotation for this affiliate {self.affiliate.company_name} / #{self.affiliate.id}')

        try:
            cap_folder, advertiser_lead_id, auto_login = caps.send(self)
        except RotationDoesNotExist as e:
            PushingErrorLog.objects.create(
                trafficdata=self,
                message=e
            )
            if raise_exception:
                raise PushLeadException(e)
            return False
        except AdvertiserRejectedException as e:
            if raise_exception:
                raise PushLeadException(e)
            return False

        message = 'Log after pushing:\n'
        for i, cap in enumerate(caps):
            message += f'{i+1}. {cap.advertiser.name} #{cap.advertiser.id} CAP #{cap.id}\n\n'

        # add Registered to: advertiser name
        message += f'>> Registered to: {cap_folder.advertiser.name} #{cap_folder.advertiser.id}'

        PushingAttemptLog.objects.create(
            trafficdata=self,
            message=message,
        )

        advertiserfolder = cap_folder.parent
        message = f'Lead {self.id} pushed to advertiser {advertiserfolder.advertiser.name} #{advertiserfolder.id} CAP #{cap_folder.id}'
        self.advertiser_accepted(
            description=message,
            advertiser_external_id=advertiser_lead_id,
            advertiser_id=advertiserfolder.advertiser.id,
            auto_login_url=auto_login,
        )
        self.save()

        return True

    def get_serialized_data(self):
        from .serializers import TrafficDataPublicSerializer
        fields = self._get_profile_fields()
        return TrafficDataPublicSerializer(self, profile_fields=fields).data

    @ property
    def time_since_click(self):
        return self.click_landed_created_at - self.click_created_at if self.click_landed_created_at else timedelta(seconds=0)

    @ property
    def time_since_lead(self):
        return self.sale_created_at - self.lead_created_at if self.sale_created_at else timedelta(seconds=0)

    @ property
    def time_since_auto_login(self):
        return self.auto_login_created_at - self.lead_created_at if self.auto_login_created_at else timedelta(seconds=0)

    @ property
    def payout(self):
        return self.conversions.payout()

    @ property
    def revenue(self):
        return self.conversions.revenue()

    def is_late(self):
        return self.time_since_lead > timedelta(days=1)

    def create_event(self, event_name: str):
        try:
            return self.event_logs.create_event_log(event_name, self)
        except Exception as e:
            self.debug(f'Event log error: {e} {event_name}')
            raise e


class Click(TrafficData):
    '''
    Click Proxy Model
    '''
    objects = ClickManager()

    class Meta:
        """Meta definition for Click."""

        verbose_name = 'Click'
        verbose_name_plural = 'Clicks'

        proxy = True


class Lead(TrafficData):
    '''
    Lead Proxy Model
    '''
    objects = LeadManager()

    class Meta:
        """Meta definition for Lead."""

        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'

        proxy = True


class Sale(TrafficData):
    '''
    Sale Proxy Model
    '''
    objects = SaleManager()

    class Meta:
        """Meta definition for Sale."""

        verbose_name = 'Sale'
        verbose_name_plural = 'Sales'

        proxy = True


class AffiliateClick(TrafficData):
    '''
    Affiliate Click Proxy Model
    '''
    objects = AffiliateClickManager()

    class Meta:
        verbose_name = 'Click'
        verbose_name_plural = 'Clicks'

        proxy = True

    @ property
    def advertiser_sale_status(self):
        if self.is_risky:
            return self.afm_status
        return super().advertiser_sale_status

    def get_state(self):
        return self.afm_state

    @ property
    def advertiser_sale_status(self):
        return self.afm_status

    def get_state_display(self):
        return self.get_afm_state_display()

    def get_state(self):
        return self.afm_state

    def __str__(self):
        return f'{self.id}'


class AffiliateLead(TrafficData):
    '''
    Affiliate Lead Proxy Model
    '''
    objects = AffiliateLeadManager()

    class Meta:
        """Meta definition for AffiliateLeadProxy."""

        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'

        proxy = True

    @ property
    def advertiser_sale_status(self):
        return self.afm_status

    def get_state_display(self):
        return self.get_afm_state_display()

    def get_state(self):
        return self.afm_state

    def __str__(self):
        return f'{self.id}'


class AffiliateSale(TrafficData):
    '''
    Affiliate Sale Proxy Model
    '''
    objects = AffiliateSaleManager()

    class Meta:
        """Meta definition for AffiliateSaleProxy."""

        verbose_name = 'Sale'
        verbose_name_plural = 'Sales'

        proxy = True

    def get_state_display(self):
        return self.get_afm_state_display()

    def get_state(self):
        return self.afm_state

    def __str__(self):
        return f'{self.id}'


class Conversion(models.Model):
    '''
    Conversion Model
    '''
    objects = ConversionQuerySet.as_manager()

    trafficdata = models.ForeignKey(
        TrafficData, on_delete=models.CASCADE, related_name='conversions')
    payout = MoneyField(max_digits=14, decimal_places=2,
                        default_currency='USD', default=Money(0, 'USD'))
    revenue = MoneyField(max_digits=14, decimal_places=2,
                         default_currency='USD', default=Money(0, 'USD'))
    tid = models.CharField(max_length=255, blank=True,
                           null=True)  # transaction id
    goal = models.ForeignKey(
        'settings.Goal', on_delete=models.CASCADE, related_name='conversions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta definition for Conversion."""
        verbose_name = 'Conversion'
        verbose_name_plural = 'Conversions'
        unique_together = ('trafficdata', 'tid')

    @property
    def executed_risk(self):
        if hasattr(self.trafficdata, 'executed_risk'):
            return self.trafficdata.executed_risk

    @property
    def is_late(self) -> bool:
        # check if conversion is late or not - if conversion is late it means that it was created after 24 hours of click
        if self.created_at > self.trafficdata.created_at + timedelta(hours=24):
            return True
        return False

    def __str__(self):
        return f'{self.id}'
