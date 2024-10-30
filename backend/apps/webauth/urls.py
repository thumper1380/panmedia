from django.urls import path, include
from .views import WebAuthRegistrationViewSet, WebAuthnAuthenticationViewSet
from rest_framework import routers
# Settings
api = routers.DefaultRouter()
api.trailing_slash = '/?'


router = routers.DefaultRouter()

urlpatterns = [
    path('register/', WebAuthRegistrationViewSet.as_view({'get': 'register', 'post': 'verify'})),
    path('authenticate/', WebAuthnAuthenticationViewSet.as_view({'get': 'authenticate', 'post': 'verify'})),
]
