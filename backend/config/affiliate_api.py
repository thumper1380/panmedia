from django.urls import path, include
from rest_framework import routers
from apps.affiliate_api.views import AffiliateAPIViewSet
# Settings
api = routers.DefaultRouter()
api.trailing_slash = '/?'

# Users API
api.register(r'affiliate', AffiliateAPIViewSet, basename='affiliate')
# APIView for TrafficData


urlpatterns = [
    path('', include(api.urls)),
]
