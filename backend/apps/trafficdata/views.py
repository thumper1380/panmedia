# Create your views here.
from django import forms
from datetime import datetime

from apps.traffic_distribution.exceptions import RotationDoesNotExist
from .serializers import TrafficDataLogPolymorphicSerializer, AdvertiserSaleStatusSerializer
from rest_framework.exceptions import MethodNotAllowed
import django_filters
from apps.utils.search import SearchMultipleModelsViewSet
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotFound, HttpResponseBadRequest, HttpResponse
from django.db import IntegrityError

# rest framework imports
from rest_framework.decorators import action
from rest_framework import status, viewsets
from rest_framework.response import Response

from django_fsm import TransitionNotAllowed


# 3rd party imports
from ipware import get_client_ip
import phonenumbers

# models
from .models import Click, Lead, Sale, TrafficData
from .states import StateChoices
from apps.settings.models import CRMSettings, Event

# serializers
from .serializers import ClickSerializer, LeadSerializer, SaleSerializer, TrafficDataSerializer, TrafficDataTableSerializer, TrafficDataDetailSerializer
from apps.settings.serializers import FormSerializer, LeadFlowSerializer
from apps.affiliate.serializers import PixelSerializer

from apps.utils.responses import ErrorResponse, SuccessResponse, ValidationErrorResponse

# test
from apps.utils.views import DrillDownAPIView
# from rest_framework_drilldown import DrillDownAPIView
import requests

class LeadViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Lead.objects.all()
        serializer = LeadSerializer(queryset, many=True)
        return Response(serializer.data)


    @action(detail=False, methods=['GET'], url_path='pan.js')
    def pan_js(self, request):
        from django.conf import settings
        from django.http import FileResponse, Http404
        import os
        try:
            pan_js_file_path = os.path.join(
                settings.STATIC_ROOT, 'js', 'pan.js')
            return FileResponse(open(pan_js_file_path, 'rb'), content_type='application/javascript')
        except FileNotFoundError:
            raise Http404("File not found.")





class TrafficDataList(DrillDownAPIView):
    """A GET API for Invoice objects"""
    # Primary model for the API (required)
    model = TrafficData

    # Global throttle for the API. Defaults to 1000. If your query hits MAX_RESULTS,
    # this is noted in X-Query_Warning in the response header.
    MAX_RESULTS = 100

    # The picky flag defaults to False; if True, then any unidentifiable param in the
    # request will result in an error.
    picky = True

    # Optional list of chained foreignKey, manyToMany, and oneToOne objects
    # your users can drill down into -- note that you do not need to build
    # separate serializers for these; DrilldownAPI builds them dynamically.
    drilldowns = ['affiliate', 'funnel', 'country__code']

    # Optional list of fields to ignore if they appear in the request
    # ignore =

    # Optional list of fields that your users are not allowed to
    # see or query
    # hide = ['salesperson__commission_pct']

    def get_base_query(self):
        # Base query for your class, typically just '.objects.all()'
        queryset = TrafficData.objects.all()
        print('Count: ', queryset.count())
        return queryset


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer


lead_list = LeadViewSet.as_view({'get': 'list'})


traffic_data_list = TrafficDataList.as_view()


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class CharFilterInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class UnixEpochDateFromToRangeFilter(django_filters.Filter):
    def filter(self, qs, value):
        if value in ([], (), {}, None, ''):
            return qs
        # Split the value into start and end timestamps
        timestamps = value.split(',')
        if len(timestamps) != 2:
            raise forms.ValidationError(
                "You must provide two comma-separated timestamps.")

        # Convert timestamps to datetimes
        start_date = datetime.fromtimestamp(int(timestamps[0]) / 1000)
        end_date = datetime.fromtimestamp(
            int(timestamps[1]) / 1000).replace(hour=23, minute=59, second=59)

        if self.distinct:
            qs = qs.distinct()

        lookup = '%s__range' % self.field_name
        return qs.filter(**{lookup: (start_date, end_date)})


class TrafficDataFilter(django_filters.FilterSet):
    state = CharFilterInFilter(field_name='state', lookup_expr='in')
    country = CharFilterInFilter(field_name='country', lookup_expr='in')
    affiliate = CharFilterInFilter(field_name='affiliate', lookup_expr='in')
    advertiser = CharFilterInFilter(field_name='advertiser', lookup_expr='in')
    created_at = UnixEpochDateFromToRangeFilter(
        field_name='created_at', lookup_expr='range')

    class Meta:
        model = TrafficData
        fields = ['state', 'country', 'affiliate', 'advertiser', 'created_at']


class TrafficDataModelViewSet(viewsets.ModelViewSet):
    queryset = TrafficData.objects.all()
    serializer_class = TrafficDataTableSerializer
    pagination_class = Pagination
    ordering_fields = ['created_at',]
    filter_backends = [DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter]
    filterset_class = TrafficDataFilter
    # search
    search_fields = ['id']  # TODO: add more search fields

    @action(detail=True, methods=['get'], url_path='state-log', url_name='state-log',)
    def state_log(self, request, pk=None):
        traffic_data: TrafficData = self.get_object()
        return Response(TrafficDataLogPolymorphicSerializer(traffic_data.logs.all(), many=True).data)

    # sale-status-log
    @action(detail=True, methods=['get'], url_path='sale-status-log', url_name='sale-status-log',)
    def sale_status_log(self, request, pk=None):
        traffic_data: TrafficData = self.get_object()
        queryset = traffic_data.advertiser_sale_statuses.all().order_by('-created_at')
        return Response(AdvertiserSaleStatusSerializer(queryset, many=True).data)

    def retrieve(self, request, pk=None):
        queryset = TrafficData.objects.all()
        traffic_data = get_object_or_404(queryset, pk=pk)
        cols = TrafficDataDetailSerializer.get_column_info()
        return SuccessResponse(data=TrafficDataDetailSerializer(traffic_data).data, columns=cols)

    @action(detail=False, methods=['get'])
    def columns(self, request):
        """
        Endpoint to retrieve column configurations for the TrafficData table.
        """
        filterable_fields = TrafficDataFilter.base_filters.keys()
        return Response(TrafficDataTableSerializer.get_column_info(filterable_fields=filterable_fields))


class SearchViewSet(SearchMultipleModelsViewSet):
    models = [TrafficData]
    serializers = [TrafficDataSerializer]

    # search
    search_fields = ['id',]
    ordering_fields = ['created_at',]
