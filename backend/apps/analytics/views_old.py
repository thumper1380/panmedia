from django.shortcuts import render

# Create your views here.
from apps.trafficdata.models import Lead, Sale, Click, TrafficData
from apps.affiliate.models import Affiliate
from django.db.models import Q, Count, Sum, Case, When, F, FloatField, ExpressionWrapper, Value, DecimalField, Window, CharField
from djmoney.models.fields import MoneyField, Money
from django.db.models.functions import Coalesce, TruncMonth, TruncDay, TruncYear, TruncWeek, Abs, TruncTime, TruncDate

from apps.trafficdata.types import CLICK, CLICK_LANDED, LEAD, LEAD_PUSHED, LEAD_DECLINED, SALE

from apps.trafficdata.models import TimeRange, StateChoices

from apps.settings.models import CRMSettings, CRMTerm
from itertools import groupby


fields_dict = {
    'clicks_count': Count('id'),
    'leads_count': Count('id', filter=Q(state=StateChoices.LEAD) | Q(state=StateChoices.LEAD_PUSHED)),
    'sales_count': Count('id', filter=Q(state=SALE)),
    'click_to_lead': Case(
        When(clicks_count=0, then=0),
        default=F('leads_count')*100/F('clicks_count'), output_field=DecimalField()),
    'revenue': Sum('revenue', filter=Q(state='sale'),
                   output_field=MoneyField(), default=Value(0)),
    'conversion_rate': Case(
        When(leads_count=0, then=0),
        default=F('sales_count')*100/F('leads_count'), output_field=DecimalField()),
    'payout': Sum('payout', filter=Q(state='sale'),
                  output_field=MoneyField(), default=Value(0)),
}


def generate_drilldown_report(model, fields, queryset):
    if not fields:
        return {}
    field = fields[0]
    grouped_queryset = queryset.annotate(*fields).values(field).order_by(field).annotate(value=Sum('value'))
    result = {
        'key': field,
        'label': field.capitalize(),
        'filter': None,
        'type': None,
        'value': None,
        'values': {}
    }
    for key, group in groupby(grouped_queryset, key=lambda x: x[field]):
        result['values'][key] = {
            'id': key,
            'label': str(key),
            'value': sum(item['value'] for item in group)
        }
        if len(fields) > 1:
            result['values'][key]['values'] = generate_drilldown_report(
                model, fields[1:], queryset.filter(**{field: key}))
    return result


def dashboard(request):
    settings = CRMSettings.objects
    default_range = 'this_month'
    # get params
    _range = request.GET.get('range', default_range)

    _vs_range = TimeRange(_range).get_vs_time_range()

    time_range = TimeRange(_range).calc()
    vs_time_range = TimeRange(_vs_range).calc()

    total_clicks = TrafficData.objects.total_clicks(
        click_created_at__range=time_range)
    
    vs_total_clicks = TrafficData.objects.total_clicks(
        click_created_at__range=vs_time_range)

    total_leads = TrafficData.objects.total_leads(
        click_created_at__range=time_range)

    vs_total_leads = TrafficData.objects.total_leads(
        click_created_at__range=vs_time_range)

    total_sales = TrafficData.objects.total_sales(
        click_created_at__range=time_range)
    vs_total_sales = TrafficData.objects.total_sales(
        click_created_at__range=vs_time_range)

    # sum or 0
    total_revenue = TrafficData.objects.filter(
        Q(state=SALE), click_created_at__range=time_range).aggregate(Sum('revenue'))['revenue__sum']
    vs_total_revenue = TrafficData.objects.filter(
        Q(state=SALE), click_created_at__range=vs_time_range).aggregate(Sum('revenue'))['revenue__sum']

    total_payout = TrafficData.objects.filter(
        Q(state=SALE), click_created_at__range=time_range).aggregate(Sum('payout'))['payout__sum']
    vs_total_payout = TrafficData.objects.filter(
        Q(state=SALE), click_created_at__range=vs_time_range).aggregate(Sum('payout'))['payout__sum']

    conversion_rate = 0 if not total_leads else total_sales * 100 / total_leads
    # total_profit = TrafficData.objects.filter(Q(state=SALE)).aggregate(Sum('profit'))['profit__sum']
    # get top 5 countries

    # calculate top countries by time range

    country_table = TrafficData.objects.top_countries(
        click_created_at__range=time_range)

    affiliates_table = TrafficData.objects.top_affiliates(
        click_created_at__range=time_range)

    advertisers_table = TrafficData.objects.top_advertisers(
        click_created_at__range=time_range)


    # use group by to create drilldown report

    # report = generate_drilldown_report(
    #     TrafficData, ['affiliate'], TrafficData.objects.all())

    # daily details view for each day in the month

    daily_clicks = TrafficData.objects.filter(Q(state=CLICK) | Q(state=CLICK_LANDED) | Q(state=LEAD) | Q(state=LEAD_PUSHED) | Q(state=SALE))\
        .annotate(date=TruncDay('click_created_at')).values('date').annotate(
        clicks_count=Count('date'),
        leads_count=Count('date', filter=Q(state=LEAD) |
                          Q(state=LEAD_PUSHED) | Q(state=SALE)),
        sales_count=Count('date', filter=Q(state=SALE)),
        click_to_lead=Case(
            When(clicks_count=0, then=0),
            default=F('leads_count')*100/F('clicks_count'), output_field=DecimalField()),
        revenue=Sum('revenue', filter=Q(state='sale'),
                    output_field=MoneyField(), default=Value(0)),
        conversion_rate=Case(
            When(leads_count=0, then=0),
            default=F('sales_count')*100/F('leads_count'), output_field=DecimalField()),
    ).order_by('date')

    sales_table = TrafficData.objects.filter(Q(state=SALE), click_created_at__range=time_range).annotate(
        date=TruncDate('sale_created_at')).values('id').annotate(
        date=F('sale_created_at'),
        affiliate=Case(
            When(affiliate__isnull=True, then=Value('No Affiliate')),
            default=F('affiliate__company_name'), output_field=CharField()),
        advertiser=Case(
            When(advertiser__isnull=True, then=Value('No Advertiser')),
            default=F('advertiser__name'), output_field=CharField()),
        country=Case(
            When(country__isnull=True, then=Value('No Country')),
            default=F('country'), output_field=CharField()),
        payout=Case(
            When(payout__isnull=True, then=Value(0)),
            default=F('payout'), output_field=MoneyField()),
        revenue=Case(
            When(revenue__isnull=True, then=Value(0)),
            default=F('revenue'), output_field=MoneyField()),
        profit=Case(
            When(revenue__isnull=True, then=Value(0)),
            default=F('revenue')-F('payout'), output_field=MoneyField()),
        funnel=Case(
            When(funnel__isnull=True, then=Value('No Funnel')),
            default=F('funnel__name'), output_field=CharField()),

    ).order_by('-date')[:10]

    context = {
        'range': _range,
        'vs_range': _vs_range,

        'total_clicks': total_clicks,
        'vs_total_clicks': vs_total_clicks,

        'total_leads': total_leads,
        'vs_total_leads': vs_total_leads,

        'total_sales': total_sales,
        'vs_total_sales': vs_total_sales,

        'total_revenue': total_revenue or 0,
        'vs_total_revenue': vs_total_revenue or 0,

        'total_payout': total_payout or 0,
        'vs_total_payout': vs_total_payout or 0,

        'conversion_rate': conversion_rate,

        'daily_clicks': daily_clicks,

        'country_table': country_table,
        'affiliate_table': affiliates_table,
        'advertiser_table': advertisers_table,

        'sales_table': sales_table,

        # 'drilldown_table': report,

    }

    context = CRMTerm.objects.calculate(context)

    print(context)
    return render(request, 'dashboard.html', context)




from rest_framework import viewsets

