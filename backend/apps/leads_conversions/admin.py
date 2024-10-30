from django.utils.safestring import mark_safe
from django.contrib import admin
from polymorphic_tree.admin import PolymorphicMPTTChildModelAdmin, PolymorphicMPTTParentModelAdmin



from .models import Payouts, PayoutAffiliateFolder, PayoutCountryFolder, PayoutAdvertiserFolder, PayoutFolder
# from apps.traffic_distribution.models import AffiliateFolder, CountryFolder, AdvertiserFolder


class PayoutsChildAdmin(PolymorphicMPTTChildModelAdmin):

    base_model = Payouts

    GENERAL_FIELDSET = (None, {
        'fields': ('name', 'parent'),
    })

    base_fieldsets = (
        GENERAL_FIELDSET,
    )

    show_in_index = False

    def has_module_permission(self, request):
        return False


class PayoutParentAdmin(PolymorphicMPTTParentModelAdmin):
    polymorphic_list = True

    base_model = Payouts
    child_models = (
        Payouts,
        PayoutAffiliateFolder,
        PayoutCountryFolder,
        PayoutAdvertiserFolder,
        PayoutFolder,
    )
    list_display = ('get_name',)

    class Media:
        css = {
            'all': ('admin/treenode/admin.css',)
        }

    def get_name(self, obj):
        level = obj.level
        to_indent = level
        return mark_safe(f'<span style="display: flex; align-items:center; margin-left: {level*15}px">{obj.name}</span>')

    def get_type(self, obj):
        # first letter uppercase
        polymorphic_obj = obj.get_real_instance()
        return polymorphic_obj.__class__.__name__

    def get_img_by_type(self, obj):
        _type = self.get_type(obj)
        if _type == 'PayoutAffiliateFolder':
            return mark_safe('<img style="margin-right:5px" src="https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/RB.svg" width="15" height="15" />')
        elif _type == 'PayoutAdvertiserFolder':
            return mark_safe('<img style="margin-right:5px" src="https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/A.svg" width="15" height="15" />')
        elif _type == 'PayoutCountryFolder':
            return mark_safe('<img style="margin-right:5px" src="https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/AB.svg" width="15" height="15" />')
        elif _type == 'PayoutFolder':
            return mark_safe('<img style="margin-right:5px" src="https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/Payout.svg" width="15" height="15" />')
        return ''

    def get_name(self, obj):
        level = obj.level
        to_indent = level
        name = obj.name
        return mark_safe(f'<span style="display: flex; align-items:center; margin-left: {level*15}px">{self.get_img_by_type(obj)}&nbsp;&nbsp;{name}</span>')





admin.site.register(Payouts, PayoutParentAdmin)
admin.site.register(PayoutAffiliateFolder, PayoutsChildAdmin)
admin.site.register(PayoutCountryFolder, PayoutsChildAdmin)
admin.site.register(PayoutAdvertiserFolder, PayoutsChildAdmin)
admin.site.register(PayoutFolder, PayoutsChildAdmin)



from .models import RevenueAdvertiserFolder, RevenueAffiliateFolder, RevenueCountryFolder, RevenueFolder, Revenues

class RevenueChildAdmin(PolymorphicMPTTChildModelAdmin):

        base_model = Revenues

        GENERAL_FIELDSET = (None, {
            'fields': ('name', 'parent'),
        })

        base_fieldsets = (
            GENERAL_FIELDSET,
        )

        show_in_index = False

        def has_module_permission(self, request):
            return False



class RevenueParentAdmin(PolymorphicMPTTParentModelAdmin):
    polymorphic_list = True

    base_model = Revenues
    child_models = (
        Revenues,
        RevenueAffiliateFolder,
        RevenueCountryFolder,
        RevenueAdvertiserFolder,
        RevenueFolder
    )
    list_display = ('get_name',)

    class Media:
        css = {
            'all': ('admin/treenode/admin.css',)
        }

    def get_img_by_type(self, obj):
        _type = self.get_type(obj)
        if _type == 'RevenueAffiliateFolder':
            return mark_safe('<img style="margin-right:5px" src="https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/RB.svg" width="15" height="15" />')
        elif _type == 'RevenueAdvertiserFolder':
            return mark_safe('<img style="margin-right:5px" src="https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/A.svg" width="15" height="15" />')
        elif _type == 'RevenueCountryFolder':
            return mark_safe('<img style="margin-right:5px" src="https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/AB.svg" width="15" height="15" />')
        elif _type == 'RevenueFolder':
            return mark_safe('<img style="margin-right:5px" src="https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/Revenue.svg" width="15" height="15" />')
        return ''

    def get_name(self, obj):
        level = obj.level
        to_indent = level
        name = obj.name if self.get_type(obj) != 'RevenueFolder' else 'Revenue'
        return mark_safe(f'<span style="display: flex; align-items:center; margin-left: {level*15}px">{self.get_img_by_type(obj)}&nbsp;&nbsp;{name}</span>')

    def get_type(self, obj):
        # first letter uppercase
        polymorphic_obj = obj.get_real_instance()
        return polymorphic_obj.__class__.__name__



admin.site.register(Revenues, RevenueParentAdmin)
admin.site.register(RevenueAffiliateFolder, RevenueChildAdmin)
admin.site.register(RevenueCountryFolder, RevenueChildAdmin)
admin.site.register(RevenueAdvertiserFolder, RevenueChildAdmin)
admin.site.register(RevenueFolder, RevenueChildAdmin)


