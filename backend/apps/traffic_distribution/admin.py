from .models import PullConversionsRequest, PullLeadsRequest, PushLeadRequest, Header
from django.utils.safestring import mark_safe
from .models import RotationControl, RotationContolAffiliateFolder, RotationControlCountryFolder, RotationControlAdvertiserFolder, RotationControlAdvertiserSplit, RotationControlCountrySplitFolder, RotationControlAffiliateSplitFolder, CapFolder
from django.contrib import admin
from .models import Provider, Advertiser, APIConnection, Settings, SaleStatusMapping, Unassigned, Assigned, SettingsTemplate, GroupTemplate, Response, ResponseKey
from polymorphic_tree.admin import PolymorphicMPTTParentModelAdmin, PolymorphicMPTTChildModelAdmin
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline


class SettingsTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)

    def get_type(self, obj):
        return obj.__class__.__name__


class SettingsTemplateTabularInline(NestedTabularInline):
    model = SettingsTemplate
    extra = 0
    # fields = ('key', 'value', 'type', 'label', 'placeholder', 'api_connection',)


class GroupTemplateTabularInline(NestedTabularInline):
    model = GroupTemplate
    extra = 0
    inlines = [SettingsTemplateTabularInline, ]


class ResponseKeyTabularInline(NestedTabularInline):
    model = ResponseKey
    extra = 0


class ResponseTabularInline(NestedStackedInline):
    model = Response
    extra = 0
    inlines = [ResponseKeyTabularInline, ]


# class RequestHeaderTabularInline(NestedTabularInline):
#     model = RequestHeader
#     extra = 0


# class RequestTabularInline(NestedStackedInline):
#     model = Request
#     extra = 0
#     #not editable
#     # readonly_fields = ('label',)
#     inlines = [RequestHeaderTabularInline, ResponseTabularInline]


class HeaderTabularInline(NestedTabularInline):
    model = Header
    extra = 0


class PullConversionsRequestTabularInline(NestedStackedInline):
    model = PullConversionsRequest
    extra = 0
    inlines = [HeaderTabularInline, ResponseTabularInline, ]


class PullLeadsRequestTabularInline(NestedStackedInline):
    model = PullLeadsRequest
    extra = 0
    inlines = [HeaderTabularInline, ResponseTabularInline, ]


class PushLeadRequestTabularInline(NestedStackedInline):
    model = PushLeadRequest
    extra = 0
    inlines = [HeaderTabularInline, ResponseTabularInline, ]


class ProviderAdmin(NestedModelAdmin):
    list_display = ('id', 'name',)

    inlines = [GroupTemplateTabularInline, PullConversionsRequestTabularInline,
               PullLeadsRequestTabularInline, PushLeadRequestTabularInline]


from django import forms
class SettingsForm(forms.ModelForm):
    # setting_template = forms.ModelChoiceField(queryset=SettingsTemplate.objects.all(), to_field_name='name')

    class Meta:
        model = Settings
        fields = ['value']


class SettingsAdmin(admin.ModelAdmin):
    # form = SettingsForm
    # list_display = ('id', 'value', 'type')
    # list_filter = ('status', 'created_at', 'updated_at')
    # search_fields = ('email', 'phone')

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Settings'}
        return super(SettingsAdmin, self).changelist_view(request, extra_context=extra_context)





class UnassignedAdmin(admin.ModelAdmin):
    list_display = ('id', 'label')
    # def get_state(self, obj):
    #     return obj.get_state_display()


class UnassignedInline(NestedTabularInline):
    model = Unassigned
    extra = 0
    # not editable
    # readonly_fields = ('label',)

    def get_state(self, obj):
        return obj.get_state_display()
    


class AssignedInline(NestedTabularInline):
    model = Assigned
    extra = 0    

class SaleStatusMappingTabularInline(NestedTabularInline):
    model = SaleStatusMapping
    extra = 0

    # note editables
    inlines = [AssignedInline, ]


class SettingsTabularInline(NestedTabularInline):
    model = Settings
    readonly_fields = ('template',)
    
    fields = ['template', 'value']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class APIConnectionTabularInline(NestedTabularInline):
    readonly_fields = ('group_template',)
    # fields = ('group_template_name',)
    model = APIConnection
    # extra = 0
    inlines = [SettingsTabularInline, ]
    # # verbose_name_plural = ''

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


from .models import AdvertiserRequiredField 
class AdvertiserRequiredFieldTabularInline(NestedTabularInline):
    model = AdvertiserRequiredField
    extra = 0



class AdvertiserAdmin(NestedModelAdmin):
    list_display = ('id', 'name', 'is_active', 'provider',
                    'default_currency', 'created_at')
    search_fields = ('name', 'provider')

    readonly_fields = ('created_at',)
    inlines = [APIConnectionTabularInline,
               SaleStatusMappingTabularInline, UnassignedInline, AdvertiserRequiredFieldTabularInline]
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        # After related objects have been saved, we can delete Unassigned instances
        for assigned in form.instance.sale_status_mappings.all():
            for a in assigned.assigned.all():
                Unassigned.objects.filter(label=a.label, advertiser=form.instance).delete()


# admin.site.register(GroupTemplate, GroupTemplateAdmin)
# admin.site.register(SettingsTemplate, SettingsTemplateAdmin)
# admin.site.register(APIConnection, APIConnectionAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(Advertiser, AdvertiserAdmin)


class RotationControChildAdmin(PolymorphicMPTTChildModelAdmin):
    base_model = RotationControl

    GENERAL_FIELDSET = (None, {
        'fields': ('name', 'parent'),
    })

    base_fieldsets = (
        GENERAL_FIELDSET,
    )

    def has_module_permission(self, request):
        return False


class RotationControlParentAdmin(PolymorphicMPTTParentModelAdmin):
    base_model = RotationControl
    child_models = (
        RotationContolAffiliateFolder,
        RotationControlCountryFolder,
        RotationControlAdvertiserFolder,
        RotationControlAdvertiserSplit,
        RotationControlCountrySplitFolder,
        RotationControlAffiliateSplitFolder,
        CapFolder
    )

    list_display = ('get_name', 'get_description', 'get_type')

    class Media:
        css = {
            'all': ('css/mptt_admin.css',)
        }

    def get_type(self, obj):
        # first letter uppercase
        polymorphic_obj = obj.get_real_instance()
        return polymorphic_obj.__class__.__name__

    get_type.short_description = 'Type'

    def get_img_by_type(self, obj):
        _type = self.get_type(obj)
        polymorphic_obj: RotationControl = obj.get_real_instance()
        if polymorphic_obj.is_active:
            return mark_safe(f'<img style="margin-right:5px" src="{polymorphic_obj.icon}" width="15" height="15" />')
        else:
            # return grayed out image
            return mark_safe(f'<img style="margin-right:5px; filter: grayscale(100%);" src="{polymorphic_obj.icon}" width="15" height="15" />')

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
        if polymorphic_obj.__class__.__name__ == 'RotationControlAdvertiserSplit':
            return f'{polymorphic_obj.percentage}%'
        elif polymorphic_obj.__class__.__name__ == 'CapFolder':
            return f'{polymorphic_obj.current_amount}/{polymorphic_obj.cap_amount}'
        return ''

    get_description.short_description = ''

    get_name.short_description = 'Name'


admin.site.register(RotationControl, RotationControlParentAdmin)
admin.site.register(RotationContolAffiliateFolder, RotationControChildAdmin)
admin.site.register(RotationControlCountryFolder, RotationControChildAdmin)
admin.site.register(RotationControlAdvertiserFolder, RotationControChildAdmin)
admin.site.register(RotationControlAdvertiserSplit, RotationControChildAdmin)
admin.site.register(RotationControlCountrySplitFolder,
                    RotationControChildAdmin)
admin.site.register(RotationControlAffiliateSplitFolder,
                    RotationControChildAdmin)
admin.site.register(CapFolder, RotationControChildAdmin)
