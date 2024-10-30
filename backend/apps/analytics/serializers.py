from apps.traffic_distribution.models import Advertiser
from apps.utils.serializers import RelatedField
from djmoney.models.fields import MoneyField
from django_countries.fields import CountryField
from enum import Enum
from rest_framework import serializers

from django.utils import timezone


class AnalyticsDataSerializer(serializers.Serializer):
    title = serializers.CharField()
    value = serializers.IntegerField()
    series = serializers.ListField(
        child=serializers.ListField(
            child=serializers.FloatField()
        )
    )


class Granularity(Enum):
    HOUR = 'hour'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'


class RegistrationChartDataSerializer(serializers.Serializer):
    date = serializers.DateTimeField()
    clicks = serializers.IntegerField()
    leads = serializers.IntegerField()
    sales = serializers.IntegerField()

    def calc_categories(self, granularity: str):
        """
        Calculate the categories based on the granularity.
        if it's day granularity, it will return hours of the day
        if it's week granularity, it will return days of the week
        if it's month granularity, it will return days of the month
        if it's year granularity, it will return months of the year
        """
        if granularity == Granularity.HOUR.value:
            return ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00',
                    '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
                    '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
                    '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']
        elif granularity == Granularity.DAY.value:
            return ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                    '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                    '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
        elif granularity == Granularity.WEEK.value:
            return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        elif granularity == Granularity.MONTH.value:
            return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        elif granularity == Granularity.YEAR.value:
            # return last 2 years
            current_year = timezone.now().year
            return [str(current_year - 1), str(current_year)]

        else:
            raise ValueError(f"Unsupported granularity: {granularity}")

    def to_representation(self, instance, granularity: str):
        """
        Convert the queryset to the format expected by ApexCharts, including categories based on granularity.
        """
        # Group data by date
        grouped_data = {}
        for item in instance:
            grouped_data.setdefault(
                item['date'], {'clicks': 0, 'leads': 0, 'sales': 0})
            grouped_data[item['date']]['clicks'] += item['clicks']
            grouped_data[item['date']]['leads'] += item['leads']
            grouped_data[item['date']]['sales'] += item['sales']

        # Prepare data for ApexCharts
        chart_data = {
            'categories': [],
            'series': [
                {'name': 'Clicks', 'data': []},
                {'name': 'Leads', 'data': []},
                {'name': 'Sales', 'data': []}
            ]
        }

        for date, values in sorted(grouped_data.items()):
            if granularity == Granularity.HOUR.value:
                formatted_date = date.strftime('%H:00')
                # calculate categories names for hourly data
            elif granularity == Granularity.DAY.value:
                formatted_date = date.strftime('%d %b')
            elif granularity == Granularity.WEEK.value:
                formatted_date = date.strftime('%d %b')
            elif granularity == Granularity.MONTH.value:
                formatted_date = date.strftime('%b')
            elif granularity == Granularity.YEAR.value:
                formatted_date = date.strftime('%Y')

            else:
                raise ValueError(f"Unsupported granularity: {granularity}")

            chart_data['categories'].append(formatted_date)
            chart_data['series'][0]['data'].append(values['clicks'])
            chart_data['series'][1]['data'].append(values['leads'])
            chart_data['series'][2]['data'].append(values['sales'])

        return chart_data


# from rest_framework import serializers


class TopCountriesTableSerializer(serializers.Serializer):
    country = serializers.CharField()
    total_clicks = serializers.IntegerField()
    total_leads = serializers.IntegerField()
    total_sales = serializers.IntegerField()
    total_revenue = MoneyField()
    total_payout = MoneyField()
    total_profit = serializers.SerializerMethodField()
    click_to_lead = serializers.SerializerMethodField()
    conversion_rate = serializers.SerializerMethodField()

    def get_total_profit(self, obj) -> MoneyField:
        return obj['total_revenue'] - obj['total_payout']

    def get_click_to_lead(self, obj) -> float:
        return obj['total_leads'] / obj['total_clicks'] if obj['total_clicks'] else 0

    def get_conversion_rate(self, obj) -> float:
        return obj['total_sales'] / obj['total_leads'] if obj['total_leads'] else 0


class ModelRelatedField(serializers.DictField):
    """
    Custom field for serializing related model data in Django REST Framework.

    Args:
        model (Model): The related model.
        source (str, optional): The field name on the related model to serialize. Defaults to 'name'.
        read_only (bool, optional): Whether the field is read-only. Defaults to False.
    """

    def __init__(self, model, source='name', read_only=True, **kwargs):
        self.model = model
        self.source_field = source
        self.read_only = read_only
        super().__init__(**kwargs)

    def to_representation(self, obj):
        try:
            obj = self.model.objects.get(id=obj)
            name = getattr(obj, self.source_field)
            id_value = obj.id
        except AttributeError as e:
            if self.source_field in str(e):  # Attribute-specific error
                return self.source_field
            else:  # Unexpected error
                raise

        return {'id': id_value, 'name': name}


class PercentageField(serializers.FloatField):
    def to_representation(self, obj):
        return obj


class TopAdvertisersTableSerializer(serializers.Serializer):
    advertiser = ModelRelatedField(model=Advertiser)
    total_clicks = serializers.IntegerField()
    total_leads = serializers.IntegerField()
    total_sales = serializers.IntegerField()
    total_revenue = MoneyField()
    conversion_rate = serializers.SerializerMethodField()

    def get_conversion_rate(self, obj) -> float:
        cr = obj['total_sales'] / \
            obj['total_leads'] if obj['total_leads'] else 0
        return PercentageField().to_representation(cr)

    @classmethod
    def get_column_info(cls, filterable_fields=[]):
        fields = cls().fields.items()
        
        columns = []
        
        model_fields = {}  # Define the model_fields variable

        for field_name, serializer_field in fields:
            # Default title and type
            title = serializer_field.label or field_name.title()
            # Use the class name of the
            field_type = type(serializer_field).__name__

            # specific case for id field
            if isinstance(serializer_field, serializers.SerializerMethodField):
                field_type = 'CharField'

            # Adjust title for fields with source attribute
            source = getattr(serializer_field, 'source', field_name)
            if source in model_fields:
                model_field = model_fields[source]
                title = model_field.verbose_name if model_field.verbose_name else title
            columns.append({'title': title, 'type': field_type})
            
            
        return columns
            