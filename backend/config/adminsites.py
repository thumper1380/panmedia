from django.contrib.admin import AdminSite


class NetworkAdminSite(AdminSite):
    site_header = 'Panmedia'
    site_title = 'Panmedia'
    index_title = 'Panmedia'


class AffiliateAdminSite(AdminSite):
    site_header = 'Panmedia'
    site_title = 'Panmedia'
    index_title = 'Panmedia'



from django.contrib import admin
network_site = NetworkAdminSite(name='network_admin')
affiliate_site = AffiliateAdminSite(name='affiliate_admin')


from django_celery_beat.models import (
    IntervalSchedule,
    CrontabSchedule,
    SolarSchedule,
    ClockedSchedule,
    # PeriodicTask,
)

admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
# admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)