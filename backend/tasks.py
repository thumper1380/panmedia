import sys
import math
# from apps.trafficsource.mgid.models import Mgid, Widget, TotalWidget
from celery import shared_task
# from .mgid.models import Campaign
from django.contrib.auth import get_user_model
User = get_user_model()


# @shared_task
# def get_mgid_widgets():
#     for user in User.objects.all():
#         for ts in user.trafficsources:
#             if type(ts) == Mgid:
#                 widgets = []
#                 for campaign in ts.campaigns.all():
#                     widgets = campaign.getWidgetsWithTracker()
#                     for i, widget in enumerate(widgets):
#                         print(f'\r{math.ceil(i/len(widgets)*10000)/100}% - {len(widgets)}', end='', flush=True)
#                         _w = Widget.objects.get_or_create(
#                             _id=widget['id'], campaign=campaign)[0]

#                         _w.revenue = widget.get('rev', 0)
#                         _w.cpc = widget['cpc']
#                         _w.spent = widget['spent']
#                         _w.conv = widget.get('conv', 0)
#                         _w.clicks = widget.get('clicks', 0)
#                         _w.save()
#     TotalWidget.objects.merge()
