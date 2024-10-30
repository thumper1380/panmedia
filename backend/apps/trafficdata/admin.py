from polymorphic.admin import PolymorphicInlineSupportMixin, PolymorphicChildModelAdmin, PolymorphicParentModelAdmin, PolymorphicChildModelFilter
from django.utils.html import linebreaks
from django.http.request import HttpRequest
from .models import Conversion
from django.contrib.humanize.templatetags.humanize import naturaltime
from .models import QueueLead
from .states import QueueLeadStatusChoices
from .models import AffiliateClick, AffiliateLead, AffiliateSale
from config.adminsites import network_site, affiliate_site
from django.utils.safestring import mark_safe
from .types import *
from django.contrib import admin
from .models import Click, Lead, Sale, TrafficData, TrafficDataLog, AdvertiserSaleStatus, ExecutedPostback
from .models import PushingErrorLog, PushingAttemptLog, StateSwitchedLog, StateInitiatedLog
from .states import StateChoices, TrafficDataLogTypeChoices
# Register your models here.

from django.db.models import Q
from django_fsm_log.admin import StateLogInline

from fsm_admin.mixins import FSMTransitionMixin

from apps.settings.models import CRMSettings


class CustomStateLogInline(StateLogInline):
    extra = 0
    fields = (
        "get_transition",
        "get_source_state",
        "get_state",
        "description",
        "timestamp",
    )

    def get_source_state(self, obj):
        return obj.get_source_state_display()

    get_source_state.short_description = "Source State"

    def get_state(self, obj):
        return obj.get_state_display()

    get_state.short_description = "State"

    def get_transition(self, obj):
        # transition slug to name
        transition = obj.transition
        return transition.replace("_", " ").title()


class ExecutedPostbackInline(admin.TabularInline):
    model = ExecutedPostback
    extra = 0
    fields = ('id', 'trafficdata', 'status',
              'content', 'message', 'created_at')
    readonly_fields = ('id', 'trafficdata', 'status',
                       'content', 'message', 'created_at')

    def get_queryset(self, request):
        qs = super(ExecutedPostbackInline, self).get_queryset(
            request).order_by('-created_at')
        return qs

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def status(self, obj):
        # green if success, red if error
        if obj.status == 'success':
            color = 'green'
        else:
            color = 'red'

        return mark_safe(f'<span style="color: {color};">{obj.status.upper()}</span>')

    status.short_description = 'Status'


class Test(FSMTransitionMixin, admin.ModelAdmin):

    readonly_fields = ('affiliate', 'advertiser_external_id', 'state', 'get_country', 'funnel', 'advertiser', 'aff_sub_1', 'device_type', 'os', 'os_version', 'aff_sub_2',
                       'aff_sub_3', 'aff_sub_4', 'aff_sub_5', 'user_agent', 'get_sale_status', 'ip_address', 'get_created_at', 'get_sale_status_changed_times', 'referrer')

    def get_fields(self, request, obj=None):
        fields = ['affiliate', 'advertiser_external_id', 'state', 'get_country', 'funnel', 'ip_address',
                  'device_type', 'os', 'os_version', 'user_agent', 'referrer', 'advertiser', 'aff_sub_1', 'aff_sub_2', 'aff_sub_3', 'aff_sub_4', 'aff_sub_5', 'get_sale_status']
        return fields

    def get_created_at(self, obj):
        time_format = CRMSettings.load().time_format
        return obj.created_at.strftime(time_format)

    get_created_at.short_description = 'Created At'

    def get_country(self, obj):
        return mark_safe(f'<span style="display: inline-block;" class="c-field-value"><span style="margin-right: .5em;"><img style="vertical-align: middle" width="20" height="20" src="https://foxesmedia-ld.platform500.com/assets/new-img/flags/{obj.country.code}.png"><!----></span><span class="c-field-value__text">{obj.country.code}</span></span>')
    get_country.short_description = 'Country'

    def get_funnel(self, obj):
        return obj.funnel.name

    get_funnel.allow_tags = True
    get_funnel.short_description = 'Funnel'

    def get_affiliate(self, obj):
        return f'{obj.affiliate}/#{obj.affiliate.id}'
    get_affiliate.short_description = 'Affiliate'
    get_affiliate.allow_tags = True

    def get_advertiser(self, obj):
        if obj.advertiser:
            return f'{obj.advertiser}/#{obj.advertiser_id}'
        return '-'

    get_advertiser.short_description = 'Advertiser'

    def get_sale_status_changed_times(self, obj: TrafficData):
        return obj.sale_status_changed_times

    get_sale_status_changed_times.short_description = 'Status Changed Times'

    def get_sale_status(self, obj):
        # return obj.advertiser_sale_status
        if not obj.advertiser:
            return '-'
        # return obj.advertiser_sale_status
        adv_sale_status = obj.advertiser_sale_status
        map_status = obj.sale_statuses.filter(assigned__label=adv_sale_status)
        if obj.sale_statuses and map_status.exists():
            ss = map_status.first().sale_status
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: {ss.color}; width: 13px; height: 13px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {ss.name}</span>')

        t = mark_safe(f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: grey; width: 13px; height: 13px; border-radius: 1000px; margin-right: 0.45rem"></div>')
        return mark_safe(f'<span style="display: flex;align-items: center;">{t} {obj.advertiser_sale_status}</span>')

    def get_state(self, obj):
        state = obj.get_state_display()
        state_value = obj.get_state()
        if state_value == StateChoices.CLICK:
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #0066ff; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == StateChoices.CLICK_LANDED:
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #37c0e5; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == StateChoices.LEAD:
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #417690; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == StateChoices.LEAD_PUSHED:
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #4caf50; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == StateChoices.LEAD_DECLINED:
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #f44336; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == StateChoices.SALE:
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #7900a4; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == StateChoices.LEAD_QUEUED:
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #ff9900; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')

        return state

    get_state.short_description = 'State'

    get_sale_status.short_description = 'Sale Status'
    get_sale_status.allow_tags = True

    def get_aff_sub_1(self, obj):
        return obj.aff_sub_1

    def get_aff_sub_2(self, obj):
        return obj.aff_sub_2

    def get_aff_sub_3(self, obj):
        return obj.aff_sub_3

    def get_aff_sub_4(self, obj):
        return obj.aff_sub_4

    def get_aff_sub_5(self, obj):
        return obj.aff_sub_5

    def get_auto_login(self, obj):
        return obj.auto_login.proxy_passed if obj.auto_login else None

    get_auto_login.short_description = 'Auto Login'
    get_auto_login.boolean = True

    get_aff_sub_1.short_description = 'Aff Sub #1'
    get_aff_sub_2.short_description = 'Aff Sub #2'
    get_aff_sub_3.short_description = 'Aff Sub #3'
    get_aff_sub_4.short_description = 'Aff Sub #4'
    get_aff_sub_5.short_description = 'Aff Sub #5'

    fsm_field = ['state', ]

    inlines = [CustomStateLogInline, ExecutedPostbackInline]


class AdvertiserSaleStatusTabularInline(admin.TabularInline):
    model = AdvertiserSaleStatus
    extra = 0
    fields = ('created_at', 'status',)
    readonly_fields = ('created_at', 'status',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super(AdvertiserSaleStatusTabularInline, self).get_queryset(
            request).order_by('-created_at')
        return qs


# import polymorphic admin tabular inline


class TrafficDataLogInline(admin.TabularInline):
    model = TrafficDataLog
    extra = 0
    readonly_fields = ('get_id', 'timestamp', 'type', 'description', )
    exclude = ('color', 'description', 'created_at', 'type')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def type(self, obj):
        type = obj.get_real_instance_class()._meta.verbose_name.upper()

        return mark_safe(f'<pre><span style="display: inline-block; width: 6px; height: 6px; border: 2px solid {obj.color}; border-radius: 50%; margin-right: 5px; vertical-align: middle;"></span><span style="vertical-align: middle;">{type}</span></pre>')

    def description(self, obj):
        background_color = ''
        # get polymorphic type
        if obj.get_real_instance_class() == StateSwitchedLog:
            if obj.get_real_instance_class() == StateSwitchedLog:
                description = f'State switched from <span style="display: inline-block; padding: 2px 6px; margin: 2px; background-color: #ddd; border-radius: 4px;">{obj.source_state}</span> to <span style="display: inline-block; padding: 2px 6px; margin: 2px; background-color: #ddd; border-radius: 4px;">{obj.target_state}</span>'

        elif obj.get_real_instance_class() == StateInitiatedLog:
            background_color = '#28a74533'
            description = f'{obj.initial_state} Initiated'

        elif obj.get_real_instance_class() == PushingErrorLog:
            background_color = '#f70f0f14'
            description = f'{obj.message}'

        elif obj.get_real_instance_class() == PushingAttemptLog:
            background_color = '#f8ae6a33'
            description = f'{obj.message}'
        else:
            description = obj

        return mark_safe(f'<pre style="width: fit-content; background-color: {background_color}; padding: 0.75em; border-radius: 0.25em;">{description}</pre>')

    def timestamp(self, obj):
        # return in this format 2023-07-2122:11:34 in pre tag
        return mark_safe(f'<pre>{obj.created_at.strftime("%Y-%m-%d %H:%M:%S")}</pre>')

    def get_id(self, obj):
        # retrun with pre tag
        return mark_safe(f'<pre>{obj.id}</pre>')

    get_id.short_description = 'ID'

    def get_queryset(self, request):
        qs = super(TrafficDataLogInline, self).get_queryset(
            request).order_by('-created_at')
        return qs


class ClickAdmin(Test):
    list_display = ('id', 'get_country', 'get_state', 'score', 'get_affiliate', 'get_aff_sub_1', 'get_aff_sub_2', 'get_aff_sub_3', 'get_aff_sub_4', 'get_aff_sub_5',
                    'get_funnel', 'device_type', 'get_page_load_time', 'is_unique', 'get_created_at',)

    fsm_field = ['state', ]

    list_per_page = 15

    list_display_links = ('id', 'get_funnel', 'get_affiliate')

    list_filter = ('affiliate', )

    inlines = [TrafficDataLogInline, ]

    def __init__(self, *args, **kwargs):
        super(ClickAdmin, self).__init__(*args, **kwargs)
        # self.list_display_links = (None,/ )

    def get_page_load_time(self, obj):
        # show delta time in seconds
        total_seconds = obj.time_since_click.total_seconds()
        return f'{total_seconds:.2f} s'

    get_page_load_time.short_description = 'Page Load Time'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Clicks'}
        return super(ClickAdmin, self).changelist_view(request, extra_context=extra_context)


class LeadAdmin(Test):
    list_display = ('id', 'get_country', 'get_state', 'is_risky', 'score', 'get_auto_login', 'is_authentic', 'get_affiliate',
                    'funnel', 'get_sale_status', 'get_sale_status_changed_times', 'get_advertiser', 'is_unique', 'get_created_at')

    inlines = [TrafficDataLogInline,
               AdvertiserSaleStatusTabularInline, ExecutedPostbackInline]

    # search
    # filter
    list_filter = ('affiliate', 'funnel', 'is_risky',
                   'is_unique', 'advertiser', 'state',)

    list_per_page = 12

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Leads'}
        return super(LeadAdmin, self).changelist_view(request, extra_context=extra_context)

    fsm_field = ['state', ]

    def is_authentic(self, obj):
        if not obj.auto_login:
            return None
        if not obj.auto_login.proxy_passed:
            return None

        return obj.auto_login.is_authentic

    is_authentic.short_description = 'Authentic'
    is_authentic.boolean = True

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # this function is called when the action is called
    actions = ['repush_lead']

    def repush_lead(self, request, queryset):
        for lead in queryset:
            lead: Lead
            lead.repush(description='Repushed by admin')


class SaleAdmin(Test):
    list_display = ('id', 'get_country', 'get_is_risky', 'get_auto_login', 'get_state',
                    'funnel', 'get_sale_status', 'advertiser', 'get_is_late', 'get_created_at')

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Sales'}
        return super(SaleAdmin, self).changelist_view(request, extra_context=extra_context)

    # user can't add new sale
    def has_add_permission(self, request):
        return False

    # user can't delete sale
    def has_delete_permission(self, request, obj=None):
        return False

    fsm_field = ['state', ]

    inlines = [TrafficDataLogInline, ExecutedPostbackInline,
               AdvertiserSaleStatusTabularInline]

    def _changeform_view(self, request, object_id, form_url, extra_context):

        if '<your-action>' in request:
            # 1. check permissions
            # 2. do your thing
            print(request)

        return super()._changeform_view(request, object_id, form_url, extra_context)

    def get_actions(self, request):
        actions = super(SaleAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_is_late(self, obj):
        return obj.is_late()

    get_is_late.short_description = 'Late'
    get_is_late.boolean = True

    def get_is_risky(self, obj):
        return obj.is_risky

    get_is_risky.short_description = 'Risky'
    get_is_risky.boolean = True


class ExecutedPostbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'trafficdata', 'get_status',
                    'content', 'get_message', 'created_at')
    readonly_fields = ('trafficdata', 'status',
                       'content', 'message', 'task_id', 'created_at')

    def get_message(self, obj):
        # short message with ...
        return f'{obj.message[:50]}...' if obj.message and len(obj.message) > 50 else obj.message

    get_message.short_description = 'Message'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_status(self, obj):
        # green if success, red if error, orange if pending
        if obj.status == 'success':
            color = 'green'
        elif obj.status == 'pending':
            color = 'orange'
        else:
            color = 'red'

        return mark_safe(f'<span style="color: {color};">{obj.status.upper()}</span>')

    get_status.short_description = 'Status'

    list_per_page = 20

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Executed Postbacks'}

        return super(ExecutedPostbackAdmin, self).changelist_view(request, extra_context=extra_context)


admin.site.register(Click, ClickAdmin)
admin.site.register(Lead, LeadAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(ExecutedPostback, ExecutedPostbackAdmin)


class AffiliateAdmin(admin.ModelAdmin):
    list_per_page = 20
    fsm_field = []

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(affiliate=request.user.affiliate)


@admin.register(AffiliateClick, site=affiliate_site)
class AffiliateClickAdmin(Test, AffiliateAdmin):
    list_display = ('get_country', 'region', 'city', 'language',
                    'funnel', 'source', 'aff_sub_1', 'aff_sub_2', 'aff_sub_3', 'aff_sub_4', 'aff_sub_5')
    readonly_fields = ('get_country', 'region', 'city', 'language', 'affiliate', 'funnel', 'source', 'aff_sub_1', 'aff_sub_2', 'aff_sub_3', 'aff_sub_4', 'aff_sub_5', 'device_type',
                       'user_agent', 'os', 'os_version', 'browser', 'browser_version', 'device_model', 'ip_address', 'bot', 'connection_type', 'x_requested_with', 'isp', 'proxy', 'is_unique', 'referrer')

    inlines = [ExecutedPostbackInline, ]

    def get_fields(self, request, obj=None):
        return self.readonly_fields

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Clicks'}
        return super(AffiliateClickAdmin, self).changelist_view(request, extra_context=extra_context)


@admin.register(AffiliateLead, site=affiliate_site)
class AffiliateLeadAdmin(Test, AffiliateAdmin):
    inlines = [ExecutedPostbackInline, ]
    fsm_field = []
    list_display = ('get_country', 'get_auto_login',
                    'funnel', 'get_sale_status', 'get_created_at')

    readonly_fields = ('get_country', 'get_state', 'get_auto_login',
                       'funnel', 'get_sale_status', 'get_created_at', 'city', 'region', 'country', 'language', 'source', 'aff_sub_1', 'aff_sub_2', 'aff_sub_3', 'aff_sub_4', 'aff_sub_5', 'device_type',)

    def get_fields(self, request, obj=None):
        return self.readonly_fields


@admin.register(AffiliateSale, site=affiliate_site)
class AffiliateSaleAdmin(Test, AffiliateAdmin):
    fsm_field = []
    list_display = ('get_country', 'get_auto_login',
                    'funnel', 'get_sale_status', 'get_created_at')

    readonly_fields = ('get_country', 'get_auto_login',
                       'funnel', 'get_sale_status', 'get_created_at', 'city', 'region', 'country', 'language', 'source', 'aff_sub_1', 'aff_sub_2', 'aff_sub_3', 'aff_sub_4', 'aff_sub_5', 'device_type',)

    def get_fields(self, request, obj=None):
        return self.readonly_fields


# impor humanize


@admin.register(QueueLead)
class QueueLeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'trafficdata', 'get_country',
                    'get_status', 'get_state', 'get_time', 'get_created_at')
    readonly_fields = ('id', 'trafficdata', 'get_country', 'get_status',
                       'get_state', 'get_time', 'created_at', 'task_id')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # filter by time
        return qs.filter()

    # remove fields
    def get_fields(self, request, obj=None):
        return self.readonly_fields

    def get_created_at(self, obj):
        return naturaltime(obj.created_at)

    get_created_at.short_description = 'Created At'
    get_created_at.admin_order_field = 'created_at'

    def get_country(self, obj):
        country = obj.trafficdata.country
        return mark_safe(f'<span style="display: inline-block;" class="c-field-value"><span style="margin-right: .5em;"><img style="vertical-align: middle" width="20" height="20" src="https://foxesmedia-ld.platform500.com/assets/new-img/flags/{country.code}.png"><!----></span><span class="c-field-value__text">{country.code}</span></span>')

    def get_time(self, obj):
        # return naturaltime(obj.time)
        # return in this format 2021-03-31 12:00:00
        return obj.time.strftime("%Y-%m-%d %H:%M:%S") if obj.time else '-'

    def get_state(self, obj):
        state = obj.trafficdata.get_state_display()
        state_value = obj.trafficdata.get_state()
        if state_value == StateChoices.CLICK:
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #0066ff; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == StateChoices.CLICK_LANDED:
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #37c0e5; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == StateChoices.LEAD:
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #417690; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == StateChoices.LEAD_PUSHED:
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #4caf50; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == StateChoices.LEAD_DECLINED:
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #f44336; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == StateChoices.SALE:
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #7900a4; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == StateChoices.LEAD_QUEUED:
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #ff9900; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')

    get_time.short_description = 'Send At'

    # sort send at
    get_time.admin_order_field = 'time'

    get_country.short_description = 'Country'

    def get_status(self, obj):
        # green if success, red if error, yellow if pending
        # what color should i use for revoked?
        color = '#DDDDDD'
        if obj.status == QueueLeadStatusChoices.REVOKED:
            color = '#DDDDDD'
        if obj.status == QueueLeadStatusChoices.SUCCESS:
            color = '#4caf50'
        elif obj.status == QueueLeadStatusChoices.PENDING:
            color = '#ff9900'
        elif obj.status == QueueLeadStatusChoices.FAILED:
            color = '#f44336'
        return mark_safe(f'<span style="color: {color};">{obj.status.upper()}</span>')

    get_status.short_description = 'Status'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # add revoke function
    actions = ['revoke']

    def revoke(self, request, queryset):
        queryset.revoke()

    # def has_change_permission(self, request, obj=None):
    #     return False


@admin.register(Conversion)
class ConversionAdmin(admin.ModelAdmin):
    list_display = ('id', 'country', 'executed_risk', 'goal', 'lead', 'is_late', 'offer', 'affiliate',
                    'advertiser', 'payout', 'revenue', 'created_at')

    def is_late(self, obj) -> bool:
        return obj.is_late

    is_late.boolean = True

    def executed_risk(self, obj):
        return obj.executed_risk.id if obj.executed_risk else None

    def lead(self, obj):
        return obj.trafficdata

    def country(self, obj):
        return obj.trafficdata.country

    def affiliate(self, obj):
        return obj.trafficdata.affiliate

    def advertiser(self, obj):
        return obj.trafficdata.advertiser

    def offer(self, obj):
        return obj.trafficdata.funnel

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
