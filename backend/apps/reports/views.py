from django.shortcuts import render
from rest_framework import serializers
from rest_framework import status
from rest_framework import viewsets
from apps.utils.views import DrillDownAPIView
from apps.utils.drilldown import DrillDownAPIView as DrillDownAPIViewV2
from apps.trafficdata.models import TrafficData


class TrafficDataDrillDown(DrillDownAPIViewV2):
    """A GET API for Invoice objects"""
    # Primary model for the API (required)
    model = TrafficData

    # Global throttle for the API. Defaults to 1000. If your query hits MAX_RESULTS,
    # this is noted in X-Query_Warning in the response header.
    MAX_RESULTS = 500

    # The picky flag defaults to False; if True, then any unidentifiable param in the
    # request will result in an error.
    picky = True

    # Optional list of chained foreignKey, manyToMany, and oneToOne objects
    # your users can drill down into -- note that you do not need to build
    # separate serializers for these; DrilldownAPI builds them dynamically.
    drilldowns = [
        'affiliate', 'country', 'advertiser'
    ]

    # Optional list of fields to ignore if they appear in the request
    ignore = ['state', 'afm_state', 'afm_status']
    # Optional list of fields that your users are not allowed to
    # see or query
    # hide = ['salesperson__commission_pct']

    def get_base_query(self):
        # Base query for your class, typically just '.objects.all()'
        queryset = TrafficData.objects.all()
        return queryset
