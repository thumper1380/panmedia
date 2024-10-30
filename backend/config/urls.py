from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from apps.offer.views import OfferLandingPageView
from django.contrib import admin
from django.contrib.auth import logout
from rest_framework.documentation import include_docs_urls
from django.urls import include, path
from django.urls import re_path as url
from apps.trafficdata.views import TrafficDataList, SearchViewSet
from django.conf import settings
from django.conf.urls.static import static
from .adminsites import network_site, affiliate_site

from config.api import api
from config.affiliate_api import api as affiliate_api

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.views import generic
from django.urls import include, path


from django.template.loader import render_to_string
from rest_framework import permissions
from rest_framework import serializers

from apps.analytics.views import DashboardAnalyticsView
from apps.affiliate.permissions import IsAffiliate
# import HttpResponse
from django.http import HttpResponse

from apps.affiliate_api.docs import AffiliateApiDocs

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('affiliate/', affiliate_site.urls),
    path('logout/', logout, {'next_page': '/'}, name='logout'),
    # include api urls and affiliate api urls
    path('api/', include(api.urls)),
    path('api/', include(affiliate_api.urls), name='affiliate_api'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('api/auth/jwt/create', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/auth/jwt/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/webauth/', include('apps.webauth.urls'), name='webauth'),

    # path('api/telegram/bot/', TelegramBotView.as_view(), name='telegram_bot'),

    path('api/telegram-bot/', include('apps.telegrambot.urls')),

    # TODO: implement this
#     path('api/drilldown-report/', TrafficDataList.as_view(), name='drill_down'),

    path('api/reports/', include('apps.reports.urls')),

    # api/track/:affiliate_id/:alias
    path('api/v1/track/<str:affiliate_id>/<str:alias>/',
         OfferLandingPageView.as_view(), name='track_offer'),

    path('api/v1/tracker/', include('tracker.urls')),



    path('api/schema/', SpectacularAPIView.as_view(urlconf='config.affiliate_api'), name='schema'),

    # Optional UI:
    path('api/affiliate/docs/',
         AffiliateApiDocs.as_view(url_name='schema'), name='redoc'),

    path('api/search/', SearchViewSet.as_view({'get': 'list'}), name='search'),

    path('api/status/', lambda request: HttpResponse('ok'), name='blank_response'),
]
