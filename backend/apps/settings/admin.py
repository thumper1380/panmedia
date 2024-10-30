from .models import EventLog, EventData
from .models import Event
from .models import QueueManagement
from .models import SMSManagement, SMSAffiliateFolder, SMSAdvertiserFolder, SMSCountryFolder, SMSFolder
from django.utils.html import format_html
from django.urls import reverse
from .models import CRMSettings, SaleStatus
# import polymorphic admin
from polymorphic_tree.admin import PolymorphicMPTTChildModelAdmin, PolymorphicMPTTParentModelAdmin

# from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from .models import RiskManagement, RiskManagementAffiliateFolder, RiskManagementCountryFolder, RiskManagementAdvertiserFolder, RiskFolder
from django.utils.safestring import mark_safe
from django.contrib import admin
from .models import LeadProfile, Form, LeadFlow, CRMTerm, State, Transition, ValidationRule
from .models import ExecutedRisk, Goal, GoalType, Source
from .models import Domain
from apps.trafficdata.models import TrafficData



@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)

@admin.register(GoalType)
class GoalTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('id', 'goal_type',)


# class ValidationRulesTabularInline(admin.TabularInline):
#     model = ValidationRules
#     extra = 0


class StateTabularInline(admin.TabularInline):
    model = State
    extra = 0


class TransitionTabularInline(admin.TabularInline):
    model = Transition
    extra = 0


class LeadFlowAdmin(admin.ModelAdmin):
    inlines = [StateTabularInline, TransitionTabularInline]
    # list_display = ('name',)
    # list_filter = ('created_at', 'updated_at')
    # search_fields = ('name',)


# import nested admin


@admin.register(ValidationRule)
class ValidationRuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)


@admin.register(LeadProfile)
class LeadProfileAdmin(admin.ModelAdmin):
    ...


class LeadProfileInline(admin.TabularInline):
    model = LeadProfile
    extra = 0
    


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name',)
    # inlines = [LeadProfileInline]
    


class CRMTermsAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'type')
    # list_filter = ('status', 'created_at', 'updated_at')
    # search_fields = ('email', 'phone')

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'CRM Terms'}
        return super(CRMTermsAdmin, self).changelist_view(request, extra_context=extra_context)


# admin.site.register(LeadProfile, LeadProfileAdmin)
admin.site.register(LeadFlow, LeadFlowAdmin)
admin.site.register(CRMTerm, CRMTermsAdmin)


# impor polymorpyc mptt admin


class RiskManagementChildAdmin(PolymorphicMPTTChildModelAdmin):
    base_model = RiskManagement

    def has_module_permission(self, request):
        return False


class RiskManagementParentAdmin(PolymorphicMPTTParentModelAdmin):
    base_model = RiskManagement
    child_models = (
        RiskManagementAffiliateFolder,
        RiskManagementCountryFolder,
        RiskManagementAdvertiserFolder,
        RiskFolder
    )

    list_display = ('get_name', 'get_description', 'get_type')

    def get_type(self, obj):
        # first letter uppercase
        polymorphic_obj = obj.get_real_instance()
        name = polymorphic_obj.__class__.__name__.replace('RiskManagement', '')
        name = ''.join([c if c.islower() else " " + c for c in name]).strip()
        return name
        


    get_type.short_description = 'Type'

    def get_img_by_type(self, obj):
        _type = obj.get_real_instance().__class__.__name__

        if _type == 'RiskManagementAffiliateFolder':
            return mark_safe('<img style="margin-right:5px" src="https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/RB.svg" width="15" height="15" />')
        elif _type == 'RiskManagementAdvertiserFolder':
            return mark_safe('<img style="margin-right:5px" src="https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/A.svg" width="15" height="15" />')
        elif _type == 'RiskManagementCountryFolder':
            return mark_safe('<img style="margin-right:5px" src="https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/AB.svg" width="15" height="15" />')
        elif _type == 'RiskFolder':
            return mark_safe('<img style="margin-right:5px" src="https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/S.svg" width="15" height="15" />')
        return ''

    def get_name(self, obj):
        level = obj.level
        to_indent = level

        polymorphic_obj = obj.get_real_instance()
        name = polymorphic_obj.name
        # if polymorphic_obj.__class__.__name__ == 'AdvertiserFolder':
        #     name += f' {polymorphic_obj.percentage}%'
        # elif polymorphic_obj.__class__.__name__ == 'CapFolder':
        #     name += f' {polymorphic_obj.current_amount}/{polymorphic_obj.cap_amount}'

        # name = f'{polymorphic_obj.name} - {polymorphic_obj.weight}' if polymorphic_obj else polymorphic_obj.__class__.__name__
        return mark_safe(f'<span style="display: flex; align-items:center; margin-left: {level*15}px">{self.get_img_by_type(obj)}&nbsp;&nbsp;{name}</span>')

    def get_description(self, obj):
        polymorphic_obj = obj.get_real_instance()
        if polymorphic_obj.__class__.__name__ == 'AdvertiserFolder':
            return f'{polymorphic_obj.percentage}%'
        elif polymorphic_obj.__class__.__name__ == 'CapFolder':
            return f'{polymorphic_obj.current_amount}/{polymorphic_obj.cap_amount}'
        return ''

    get_description.short_description = ''

    get_name.short_description = 'Name'


admin.site.register(RiskManagement, RiskManagementParentAdmin)
admin.site.register(RiskManagementAffiliateFolder, RiskManagementChildAdmin)
admin.site.register(RiskManagementCountryFolder, RiskManagementChildAdmin)
admin.site.register(RiskManagementAdvertiserFolder, RiskManagementChildAdmin)
admin.site.register(RiskFolder, RiskManagementChildAdmin)


@admin.register(CRMSettings)
class CRMSettingsAdmin(admin.ModelAdmin):...
    # list_display = ('id', 'key', 'value',)

    # def changelist_view(self, request, extra_context=None):
    #     extra_context = {'title': 'CRM Settings'}
    #     return super(CRMSettingsAdmin, self).changelist_view(request, extra_context=extra_context)


@admin.register(SaleStatus)
class SaleStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description',
                    'key', 'get_color', 'created_at')

    list_display_links = ('id',)
    allow_tags = True

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Sale Status'}
        return super(SaleStatusAdmin, self).changelist_view(request, extra_context=extra_context)

    def get_color(self, obj):
        t = mark_safe(
            f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: {obj.color}; width: 15px; height: 15px; border-radius: 1000px;"></div>')
        return t
    get_color.short_description = 'Color'
    get_color.allow_tags = True


@admin.register(ExecutedRisk)
class ExecutedRiskAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_trafficdata_id', 'country',
                    'get_state', 'get_affiliate', 'get_status', 'created_at')

    list_display_links = ('id',)
    # allow_tags = True

    # filters
    list_filter = ('trafficdata__affiliate',)
    search_fields = ('trafficdata__country',)

    # def get_state(self, obj):
    #     return obj.trafficdata.state

    def get_state(self, obj):
        state = obj.get_state_display()
        state_value = obj.get_state()

        if state_value == 'click':
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #0066ff; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == 'click_landed':
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #37c0e5; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == 'lead':
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #417690; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == 'lead_pushed':
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #4caf50; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == 'lead_declined':
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #f44336; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')
        elif state_value == 'sale':
            t = mark_safe(
                f'<div class="c-field-value__shape-circle ng-star-inserted" style="background-color: #7900a4; width: 10px; height: 10px; border-radius: 1000px; margin-right: 0.45rem"></div>')
            return mark_safe(f'<span style="display: flex;align-items: center;">{t} {state}</span>')

        return state

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Executed Risk'}
        return super(ExecutedRiskAdmin, self).changelist_view(request, extra_context=extra_context)

    def get_trafficdata_id(self, obj):
        if obj.trafficdata.state == 'lead_pushed' or obj.trafficdata.state == 'lead':
            url = reverse('admin:trafficdata_lead_change',
                          args=[obj.trafficdata.id])
            return format_html('<a href="{}">{}</a>', url, obj.trafficdata.id)
        elif obj.trafficdata.state == 'click' or obj.trafficdata.state == 'click_landed':
            url = reverse('admin:trafficdata_click_change',
                          args=[obj.trafficdata.id])
            return format_html('<a href="{}">{}</a>', url, obj.trafficdata.id)
        elif obj.trafficdata.state == 'sale':
            url = reverse('admin:trafficdata_sale_change',
                          args=[obj.trafficdata.id])
            return format_html('<a href="{}">{}</a>', url, obj.trafficdata.id)

    def get_affiliate(self, obj):
        affiliate = obj.trafficdata.affiliate
        url = reverse('admin:affiliate_affiliate_change', args=[affiliate.id])
        return format_html('<a href="{}">{}</a>', url, affiliate.company_name)

    def get_status(self, obj):
        status = obj.status
        status_display = obj.get_status_display()
        # link status if it's risk so color will be yellow if it's released so color will be green
        if status == ExecutedRisk.RISK:
            return format_html('<span style="color: #FFA500;">{}</span>', status_display)
        elif status == ExecutedRisk.RELEASED:
            return format_html('<span style="color: #008000;">{}</span>', status_display)

    def release_risk(self, request, queryset):
        queryset.update(status=ExecutedRisk.RELEASED)
        trafficdata_ids = queryset.values_list('trafficdata', flat=True)
        # update the trafficdata of executed risk queryset to is_risky = False
        for trafficdata_id in trafficdata_ids:
            trafficdata: TrafficData = TrafficData.objects.get(
                id=trafficdata_id)
            trafficdata.release_risk()

        self.message_user(
            request, "Selected risks have been released successfully")

    release_risk.short_description = "Release Risk"

    actions = [release_risk]

    def get_actions(self, request):
        actions = super(ExecutedRiskAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    get_trafficdata_id.short_description = 'Lead'
    get_trafficdata_id.allow_tags = True

    get_affiliate.short_description = 'Affiliate'
    get_affiliate.allow_tags = True

    get_status.short_description = 'Status'
    get_status.allow_tags = True


class SMSManagementChildAdmin(PolymorphicMPTTChildModelAdmin):
    base_model = SMSManagement

    def has_module_permission(self, request):
        return False


class SMSManagementParentAdmin(PolymorphicMPTTParentModelAdmin):

    allow_tags = True

    base_model = SMSManagement

    child_models = (
        SMSAdvertiserFolder,
        SMSCountryFolder,
        SMSAffiliateFolder,
        SMSFolder
    )

    list_display = ('get_name', 'get_description', 'get_type')

    def get_type(self, obj):
        # first letter uppercase
        polymorphic_obj = obj.get_real_instance()
        return polymorphic_obj.__class__.__name__

    get_type.short_description = 'Type'

    def get_img_by_type(self, obj):
        return ''
        polymorphic_obj: RotationControl = obj.get_real_instance()
        return mark_safe(f'<img style="margin-right:5px" src="{polymorphic_obj.icon}" width="15" height="15" />')

    def get_name(self, obj):
        level = obj.level
        to_indent = level

        polymorphic_obj = obj.get_real_instance()
        name = polymorphic_obj.name
        # if polymorphic_obj.__class__.__name__ == 'AdvertiserFolder':
        #     name += f' {polymorphic_obj.percentage}%'
        # elif polymorphic_obj.__class__.__name__ == 'CapFolder':
        #     name += f' {polymorphic_obj.current_amount}/{polymorphic_obj.cap_amount}'

        # name = f'{polymorphic_obj.name} - {polymorphic_obj.weight}' if polymorphic_obj else polymorphic_obj.__class__.__name__
        return mark_safe(f'<span style="display: flex; align-items:center; margin-left: {level*15}px">{self.get_img_by_type(obj)}&nbsp;&nbsp;{name}</span>')

    def get_description(self, obj):
        polymorphic_obj = obj.get_real_instance()
        if polymorphic_obj.__class__.__name__ == 'AdvertiserFolder':
            return f'{polymorphic_obj.percentage}%'
        elif polymorphic_obj.__class__.__name__ == 'CapFolder':
            return f'{polymorphic_obj.current_amount}/{polymorphic_obj.cap_amount}'
        return ''

    get_description.short_description = ''

    get_name.short_description = 'Name'


admin.site.register(SMSManagement, SMSManagementParentAdmin)
admin.site.register(SMSAdvertiserFolder, SMSManagementChildAdmin)
admin.site.register(SMSCountryFolder, SMSManagementChildAdmin)
admin.site.register(SMSAffiliateFolder, SMSManagementChildAdmin)
admin.site.register(SMSFolder, SMSManagementChildAdmin)


from .models import TXTRecord

class TXTRecordInline(admin.TabularInline):
    readonly_fields = ('verification_code',)
    model = TXTRecord
    extra = 1

    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_add_permission(self, request, obj=None):
        return False

from django.urls import reverse
from django.utils.html import format_html
from django.shortcuts import redirect
from django.urls import path



@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('id', 'domain', 'is_verified', 'verify_domain_button')
    readonly_fields = ('is_verified',)
    inlines = [TXTRecordInline, ]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['domain'].help_text = format_html(
            'Please point the domain records to: <strong>{}</strong>', request.get_host()
        )
        return form

    def verify_domain_button(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green;">Verified</span>')
        else:
            url = reverse('admin:verify-domain', args=[obj.id])
            return format_html(
                '<a class="button" href="{}">Verify Domain</a>', url
            )
    verify_domain_button.short_description = 'Verification'
    verify_domain_button.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('verify-domain/<int:domain_id>/', self.verify_domain_view, name='verify-domain'),
        ]
        return custom_urls + urls

    def verify_domain_view(self, request, domain_id):
        domain = self.get_object(request, domain_id)
        # Perform domain verification logic here
        domain.is_verified = True
        domain.save()
        # Redirect back to the change form
        return redirect('admin:settings_domain_change', domain_id)
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['verify_domain_button'] = self.verify_domain_button
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    

class DomainInline(admin.TabularInline):
    model = Domain
    extra = 0


class CompanyAdmin(admin.ModelAdmin):
    inlines = [DomainInline, ]

@admin.register(QueueManagement)
class QueueManagementAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_country', 'from_hour',
                    'to_hour', 'from_day', 'to_day', 'in_queue',)

    def has_delete_permission(self, request, obj=None):
        return False

    def in_queue(self, obj):
        return obj.in_queue().count()

    def get_country(self, obj):
        if obj.is_enabled:
            return mark_safe(f'<span style="display: inline-block;" class="c-field-value"><span style="margin-right: .5em;"><img style="vertical-align: middle" width="20" height="20" src="https://foxesmedia-ld.platform500.com/assets/new-img/flags/{obj.country.code}.png"><!----></span><span class="c-field-value__text">{obj.country.code}</span></span>')
        else:
            # gray out the country
            return mark_safe(f'<span style="display: inline-block;" class="c-field-value"><span style="margin-right: .5em;"><img style="vertical-align: middle; filter: grayscale(100%);" width="20" height="20" src="https://foxesmedia-ld.platform500.com/assets/new-img/flags/{obj.country.code}.png"><!----></span><span class="c-field-value__text">{obj.country.code}</span></span>')
    get_country.short_description = 'Country'



class EventDataInline(admin.TabularInline):
    model = EventData
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_count')

    inlines = [EventDataInline, ]

    def get_count(self, obj):
        return obj.count()


@admin.register(EventLog)
class ExecutedEventAdmin(admin.ModelAdmin):
    ...




from .models import EmailTemplate   

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    ...