# from django.contrib import admin
# # mppt model admin
# from mptt.admin import MPTTModelAdmin
# # Register your models here.
# from .models import SMSCampaign, SMSListData, SMSList, SMSAdText, SMSCampaignOffer, SMSAutomation, SMSAutomationTextAd, SMSAutomationCampaign
# from apps.offer.models import Offer

# class SMSAdTextInline(admin.TabularInline):

#     model = SMSAdText
#     extra = 0


# class SMSOfferInline(admin.TabularInline):
#     model = SMSCampaignOffer
#     extra = 0


# @admin.register(SMSCampaign)
# class SMSCampaignAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'country', 'sender',)

#     inlines = [
#         SMSAdTextInline,
#         SMSOfferInline,
#     ]







# @admin.register(SMSListData)
# class SMSListDataAdmin(admin.ModelAdmin):
#     list_display = ('id', 'list', 'phone_number', 'first_name', 'last_name', 'email', 'is_valid')
    



# @admin.register(SMSList)
# class SMSListAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'contacts',)

#     def contacts(self, obj):
#         return obj.smslistdata_set.count()




# class SMSAutomationTextAdInline(admin.TabularInline):
#     model = SMSAutomationTextAd
#     extra = 0


# class SMSAutomationInline(admin.TabularInline):
#     readonly_fields = ('campaign', )
#     model = SMSAutomation
#     extra = 0
#     inlines = [
#         SMSAutomationTextAdInline
#     ]

# @admin.register(SMSAutomationCampaign)
# class SMSAutomationCampaignAdmin(admin.ModelAdmin):
#     # list_display = ('id', 'name', 'country', 'sender',)

#     inlines = [
#         SMSAutomationInline,
#     ]