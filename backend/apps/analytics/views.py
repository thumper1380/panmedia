from enum import Enum
from datetime import datetime
from rest_framework.exceptions import ValidationError
from apps.settings.models import CRMTerm
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import AnalyticsDataSerializer

from apps.trafficdata.models import TrafficData, StateChoices

from django.db.models import Count, Sum, Case, When, F, FloatField, ExpressionWrapper, Value, DecimalField
# import TruncMonth, TruncDay, TruncYear, TruncWeek, Abs, TruncTime, TruncDate
from django.db.models.functions import Cast, Coalesce, TruncMonth, TruncDay, TruncYear, TruncWeek, Abs, TruncTime, TruncDate, Trunc
# ExtractEpoch
from django.db.models.functions import Extract, ExtractDay, ExtractSecond
from django.db.models.functions import TruncTime, TruncDate, TruncDay, TruncMonth, TruncYear, TruncWeek, TruncHour
from apps.utils.db_functions import ExtractEpoch


# import rest_framework action
from rest_framework.decorators import action

from rest_framework import viewsets

from django.db.models import Q

from .mixin import DateValidationMixin
from rest_framework import status
from datetime import timedelta
from .serializers import RegistrationChartDataSerializer
from djmoney.models.fields import MoneyField


def build_querysets(start_date, end_date):
    queryset = TrafficData.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).aggregate(  # Changed from annotate to aggregate
        total_clicks=Count('id'),
        total_leads=Count('id', filter=Q(state__in=[
            StateChoices.LEAD, StateChoices.LEAD_PUSHED, StateChoices.LEAD_QUEUED, StateChoices.LEAD_DECLINED, StateChoices.SALE])),
        total_sales=Count('id', filter=Q(state=StateChoices.SALE)),



        total_clicks_landed=Count('id', filter=Q(
            state=StateChoices.CLICK_LANDED)),
        total_leads_pushed=Count('id', filter=Q(
            state=StateChoices.LEAD_PUSHED)),
        total_leads_queued=Count('id', filter=Q(
            state=StateChoices.LEAD_QUEUED)),
        total_leads_rejected=Count('id', filter=Q(
            state=StateChoices.LEAD_DECLINED)),



        total_revenue=Coalesce(Sum('conversions__revenue'),
                               0, output_field=MoneyField()),
        total_payout=Coalesce(Sum('conversions__payout'),
                              0, output_field=MoneyField()),

    )

    return queryset


def get_table_queryset(start_date: datetime, end_date: datetime, field: str, order_by: str='-total_sales') -> list:
    queryset = (
        TrafficData.objects
        .filter(created_at__range=[start_date, end_date])
        # filter field__isnull=False
        .exclude(**{f'{field}__isnull': True})
        .values(field)
        .annotate(
            total_clicks=Coalesce(Count('id', filter=Q(state__in=[
                StateChoices.CLICK, StateChoices.CLICK_LANDED, StateChoices.LEAD, StateChoices.LEAD_PUSHED, StateChoices.SALE])), 0),
            total_leads=Coalesce(Count('id', filter=Q(state__in=[
                StateChoices.LEAD, StateChoices.LEAD_PUSHED, StateChoices.LEAD_QUEUED, StateChoices.LEAD_DECLINED, StateChoices.SALE])), 0),
            total_sales=Coalesce(
                Count('id', filter=Q(state=StateChoices.SALE)), 0),
            # Fix the "MoneyField" error
            total_revenue=Coalesce(
                Sum('conversions__revenue'), 0, output_field=MoneyField()),
            total_payout=Coalesce(Sum('conversions__payout'),
                                  0, output_field=MoneyField()),
        )
        .order_by(order_by) 
    )
    return queryset


def get_registration_chart_queryset(start_date, end_date, queryset):
    queryset = (
        TrafficData.objects
        .filter(state__in=queryset, created_at__range=[start_date, end_date])
        .annotate(date=TruncMonth('created_at'))  # Truncate to month
        .values('date')  # Group by the truncated date
        .annotate(value=Count('id'))  # Count records per group
        # Convert to milliseconds
        .annotate(timestamp=ExtractEpoch('date'))
        # Convert QuerySet to list of tuples
        .values_list('timestamp', 'value')
        .order_by('date')

    )
    return list(queryset)


class Granularity(Enum):
    HOUR = 'hour'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'


class DashboardAnalyticsView(viewsets.ViewSet, DateValidationMixin):
    def initial(self, request, *args, **kwargs):
        # Call the superclass's initial method first
        super().initial(request, *args, **kwargs)
        # Perform date validation
        self.validate_dates(request)

    @action(detail=False, methods=['get'], url_path='metrics', url_name='metrics')
    def metrics(self, request, *args, **kwargs):
        # self.validate_dates(request)
        start_date = request.start_date
        end_date = request.end_date
        context = build_querysets(start_date, end_date)

        terms = CRMTerm.objects.calculate(context)

        return Response(terms)

    @action(detail=False, methods=['get'], url_path='registration-chart', url_name='registration_chart')
    def registration_chart(self, request, *args, **kwargs):
        start_date = request.start_date
        end_date = request.end_date

        granularity = self.calc_granularity(start_date, end_date)
        # return Response(granularity.value)
        data = (
            TrafficData.objects
            .filter(created_at__gte=start_date, created_at__lte=end_date)
            .annotate(
                date=Trunc('created_at', granularity.value)
            ).values('date').annotate(
                clicks=Count('id'),
                leads=Count('id', filter=Q(state__in=[
                    StateChoices.LEAD, StateChoices.LEAD_PUSHED, StateChoices.LEAD_QUEUED, StateChoices.LEAD_DECLINED, StateChoices.SALE])),
                sales=Count('id', filter=Q(state=StateChoices.SALE))

            ).order_by('date')
        )

        serialized_data = RegistrationChartDataSerializer(
        ).to_representation(data, granularity.value)
        return Response(serialized_data)

    # top countries

    @action(detail=False, methods=['get'], url_path='top-countries', url_name='top_countries')
    def top_countries(self, request, *args, **kwargs):
        # import money field from dj_money

        start_date = request.start_date
        end_date = request.end_date
        from .serializers import TopCountriesTableSerializer
        t_queryset = get_table_queryset(start_date, end_date, 'country',)

        serialized_data = TopCountriesTableSerializer(t_queryset, many=True).data

        return Response(serialized_data)
    
    
    # top advertisers
    @action(detail=False, methods=['get'], url_path='top-advertisers', url_name='top_advertisers')
    def top_advertisers(self, request, *args, **kwargs):
        start_date = request.start_date
        end_date = request.end_date
        from .serializers import TopAdvertisersTableSerializer
        t_queryset = get_table_queryset(start_date, end_date, 'advertiser',)
        from apps.traffic_distribution.models import Advertiser
        serializer = TopAdvertisersTableSerializer(t_queryset, many=True)
        columns = TopAdvertisersTableSerializer.get_column_info()
        return Response(columns)

    def calc_granularity(self, start_date: datetime, end_date: datetime) -> Granularity:
        # Calculate the difference between the two dates
        diff = end_date - start_date

        # Check for predefined date ranges and set granularity accordingly
        if start_date == end_date:
            return Granularity.HOUR
        elif diff <= timedelta(days=1):
            return Granularity.HOUR
        elif diff <= timedelta(days=7):
            return Granularity.DAY
        elif diff <= timedelta(days=30):
            return Granularity.DAY
        elif diff <= timedelta(days=365):
            return Granularity.MONTH
        else:
            return Granularity.YEAR
