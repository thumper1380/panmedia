
from django.urls import path, re_path
from .views import TrafficDataDrillDown


urlpatterns = [
    path('drilldown-report/', TrafficDataDrillDown.as_view(), name='drilldown-report'),
]
