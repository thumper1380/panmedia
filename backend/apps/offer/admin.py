from django.contrib import admin

# Register your models here.
from .models import Offer

from config.adminsites import network_site, affiliate_site


class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'language', 'active', 'created_at', 'lead_form')
    # inlines = [LeadFlowInline, ]

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Offers'}
        return super(OfferAdmin, self).changelist_view(request, extra_context=extra_context)


affiliate_site.register(Offer, OfferAdmin)

admin.site.register(Offer, OfferAdmin)
