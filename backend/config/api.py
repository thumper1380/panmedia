from rest_framework import routers
from apps.users.views import UserViewSet
from apps.trafficdata.views import LeadViewSet, TrafficDataModelViewSet
from apps.notification.views import NotificationViewSet
from apps.affiliate.views import AffiliateViewSet
from apps.settings.views import SettingsAPIView
from apps.traffic_distribution.views import AdvertiserViewSet, RotationControlViewSet
from apps.analytics.views import DashboardAnalyticsView
# Settings
api = routers.DefaultRouter()
api.trailing_slash = '/?'
api.root_view_name = 'api-root'

# Users API

api.register(r'analytics', DashboardAnalyticsView, basename='analytics')
api.register(r'users', UserViewSet)
api.register(r'affiliates', AffiliateViewSet, basename='affiliates')
api.register(r'trafficdata', TrafficDataModelViewSet, basename='trafficdata')
api.register(r'settings', SettingsAPIView, basename='settings')
api.register(r'advertisers', AdvertiserViewSet, basename='advertisers')
api.register(r'rotation-control', RotationControlViewSet, basename='rotation-control')

api.register(r'track', LeadViewSet, basename='lead')  # affiliate API
# notification API
api.register(r'notification', NotificationViewSet, basename='notification')
