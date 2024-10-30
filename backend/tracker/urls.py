# urls.py
from django.urls import path, re_path
from .views import TrackerViewSet


urlpatterns = [

    re_path(r'track/(?P<affiliate_id>\d+)/(?P<alias>\w+)',
            TrackerViewSet.as_view({'get': 'track'}), name='tracker'),
    # track/<affiliate_id>/<alias>
    
    re_path(r'track/',
            TrackerViewSet.as_view({'post': 'track'}), name='tracker'),


    # push-lead
    re_path(r'push-lead', TrackerViewSet.as_view(
        {'post': 'push_lead'}), name='push-lead'),

    # redirect
    re_path(r'redirect',
            TrackerViewSet.as_view({'get': 'redirect'}), name='autologin-redirect'),

]
