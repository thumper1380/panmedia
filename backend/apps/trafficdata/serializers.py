from apps.utils.serializers import DetailSerializer, ListSerializer, StateField, TagField, RelatedField
from .models import AdvertiserSaleStatus
from rest_polymorphic.serializers import PolymorphicSerializer
from .models import TrafficDataLog, StateSwitchedLog, StateInitiatedLog, PushingErrorLog, PushingAttemptLog
from typing import List, Tuple
from apps.offer.models import Offer
from apps.settings.models import Source
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from phonenumber_field.serializerfields import PhoneNumberField
from .models import Click, Lead, Sale, TrafficData

from rest_framework import serializers
from django_countries.serializer_fields import CountryField
# import moneyfield serializer
from djmoney.contrib.django_rest_framework import MoneyField
from drf_spectacular.utils import extend_schema_field


class TrafficDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficData
        fields = '__all__'


class ClickSerializer(serializers.ModelSerializer):
    secret = serializers.SerializerMethodField()
    country = CountryField()

    class Meta:
        model = Click
        fields = '__all__'

    def get_secret(self, obj):
        return obj.secret


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'




class MoneySerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    currency = serializers.CharField(max_length=3)


class TrafficDataPublicSerializer(serializers.ModelSerializer):
    def __init__(self, *args, profile_fields=None, **kwargs):
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        # add form fields to representation
        ret = super().to_representation(instance)
        for field in self.instance._get_profile_fields():
            try:
                # Assuming these fields are direct attributes of the instance
                ret[field] = getattr(instance, field)
            except AttributeError:
                pass  # or handle this as appropriate for your use case
        return ret

    # phone_number = PhoneNumberField()
    affiliate = serializers.SerializerMethodField()
    country = CountryField()
    country_flag = serializers.SerializerMethodField()
    advertiser = serializers.SerializerMethodField()
    funnel = serializers.SerializerMethodField()
    affiliate_id = serializers.SerializerMethodField()
    advertiser_id = serializers.SerializerMethodField()
    # payout propety
    payout = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()

    class Meta:
        model = TrafficData
        fields = ('id', 'ip_address', 'country', 'source', 'country_flag', 'aff_sub_1', 'aff_sub_2', 'aff_sub_3', 'aff_sub_4', 'aff_sub_5', 'aff_sub_6', 'aff_sub_7', 'aff_sub_8', 'aff_sub_9',
                  'aff_sub_10', 'aff_sub_11', 'aff_sub_12', 'aff_sub_13', 'aff_sub_14', 'aff_sub_15', 'aff_sub_16', 'aff_sub_17', 'aff_sub_18', 'aff_sub_19', 'aff_sub_20', 'advertiser', 'affiliate', 'affiliate_id', 'advertiser_id', 'funnel', 'payout', 'revenue')

    def get_affiliate(self, obj):
        return obj.affiliate.company_name

    def get_advertiser(self, obj):
        return obj.advertiser.name if obj.advertiser else ''

    def get_funnel(self, obj):
        return obj.funnel.name if obj.funnel else ''

    def get_country_flag(self, obj):
        # return emoji country flag code
        return get_emoji_flag(obj.country.code) if obj.country else ''

    def get_affiliate_id(self, obj):
        return obj.affiliate.id

    def get_advertiser_id(self, obj):
        return obj.advertiser.id if obj.advertiser else ''

    def get_payout(self, obj):
        return str(obj.payout)

    def get_revenue(self, obj):
        return str(obj.revenue)

    def get_phone_prefix(self, obj):
        # return phone prefix in format +44
        return '+' + str(obj.phone_number.country_code) if obj.phone_number else ''

    def get_national_number(self, obj):
        return str(obj.phone_number.national_number) if obj.phone_number else ''






class TrafficDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficData
        fields = '__all__'

    @staticmethod
    def get_field_type(field):
        # Implement your logic to determine the field type
        # Return the appropriate field type based on the field
        return 'string'

    @staticmethod
    def calc_coloumn_with(field) -> int:
        # Implement your logic to determine the field type
        # calculate column width based on field name length
        return len(field.name) * 10

    @classmethod
    def columns(cls):
        columns = []
        for field in cls.Meta.model._meta.fields:
            columns.append({
                "key": field.name,
                "title": field.verbose_name,
                "sortable": True,
                "filterable": True,
                "type": cls.get_field_type(field),
                "width": cls.calc_coloumn_with(field),
                # "resizeable": True,
            })
        return columns


class TrafficDataTableSerializer(ListSerializer):
    country = CountryField()
    state = StateField(source='get_state_display')
    affiliate = RelatedField(source='company_name', read_only=True)
    advertiser = RelatedField(read_only=True)
    is_risky = serializers.BooleanField()
    funnel = serializers.CharField(source='funnel.name')
    sale_status = TagField(source='advertiser_sale_status')
    is_unique = serializers.BooleanField()
    created_at = serializers.DateTimeField()

    class Meta:
        model = TrafficData
        fields = ['id', 'country', 'affiliate',
                  'state', 'sale_status', 'advertiser', 'funnel', 'is_risky', 'is_unique', ]

        # fields += [f'aff_sub_{i}' for i in range(1, 6)]

        fields += ['created_at']


class TrafficDataDetailSerializer(DetailSerializer):
    country = CountryField()
    state = StateField(source='get_state_display')
    affiliate = RelatedField(source='company_name', read_only=True)
    advertiser = RelatedField(read_only=True)
    is_risky = serializers.BooleanField()
    funnel = serializers.CharField(source='funnel.name')
    sale_status = TagField(source='advertiser_sale_status')
    is_unique = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    ip_address = serializers.IPAddressField()

    class Meta:
        model = TrafficData
        fields = ['id', 'country', 'affiliate',
                  'state', 'sale_status', 'advertiser', 'source', 'funnel', 'is_risky', 'is_unique', 'ip_address', 'referrer', 'device_type', 'os', 'os_version',]
        fields += [f'aff_sub_{i}' for i in range(1, 6)]
        fields += ['created_at']


class TrafficDataLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficDataLog
        fields = '__all__'


class StateSwitchedLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateSwitchedLog
        fields = '__all__'


class StateInitiatedLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateInitiatedLog
        fields = '__all__'


class PushingErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushingErrorLog
        fields = '__all__'


class PushingAttemptLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushingAttemptLog
        fields = '__all__'


class TrafficDataLogPolymorphicSerializer(PolymorphicSerializer):
    resource_type_field_name = 'type'
    model_serializer_mapping = {
        TrafficDataLog: TrafficDataLogSerializer,
        StateSwitchedLog: StateSwitchedLogSerializer,
        StateInitiatedLog: StateInitiatedLogSerializer,
        PushingErrorLog: PushingErrorLogSerializer,
        PushingAttemptLog: PushingAttemptLogSerializer
    }


# create serializer

class AdvertiserSaleStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvertiserSaleStatus
        fields = ['status', 'created_at',]


def get_emoji_flag(country_code):
    country_flags = {
        'AF': '\U0001F1E6\U0001F1EB',
        'AL': '\U0001F1E6\U0001F1F1',
        'DZ': '\U0001F1E9\U0001F1FF',
        'AD': '\U0001F1E6\U0001F1E9',
        'AO': '\U0001F1E6\U0001F1F4',
        'AG': '\U0001F1E6\U0001F1EC',
        'AR': '\U0001F1E6\U0001F1F7',
        'AM': '\U0001F1E6\U0001F1F2',
        'AU': '\U0001F1E6\U0001F1FA',
        'AT': '\U0001F1E6\U0001F1F9',
        'AZ': '\U0001F1E6\U0001F1FF',
        'BS': '\U0001F1E7\U0001F1F8',
        'BH': '\U0001F1E7\U0001F1ED',
        'BD': '\U0001F1E7\U0001F1E9',
        'BB': '\U0001F1E7\U0001F1E7',
        'BY': '\U0001F1E7\U0001F1FE',
        'BE': '\U0001F1E7\U0001F1EA',
        'BZ': '\U0001F1E7\U0001F1FF',
        'BJ': '\U0001F1E7\U0001F1EF',
        'BT': '\U0001F1E7\U0001F1F9',
        'BO': '\U0001F1E7\U0001F1F4',
        'BA': '\U0001F1E7\U0001F1E6',
        'BW': '\U0001F1E7\U0001F1FC',
        'BR': '\U0001F1E7\U0001F1F7',
        'BN': '\U0001F1E7\U0001F1F3',
        'BG': '\U0001F1E7\U0001F1EC',
        'BF': '\U0001F1E7\U0001F1EB',
        'BI': '\U0001F1E7\U0001F1EE',
        'CV': '\U0001F1E8\U0001F1FB',
        'KH': '\U0001F1F0\U0001F1ED',
        'CM': '\U0001F1E8\U0001F1F2',
        'CA': '\U0001F1E8\U0001F1E6',
        'CF': '\U0001F1E8\U0001F1EB',
        'TD': '\U0001F1F9\U0001F1E9',
        'CL': '\U0001F1E8\U0001F1F1',
        'CN': '\U0001F1E8\U0001F1F3',
        'CO': '\U0001F1E8\U0001F1F4',
        'KM': '\U0001F1F0\U0001F1F2',
        'CG': '\U0001F1E8\U0001F1EC',
        'CR': '\U0001F1E8\U0001F1F7',
        'HR': '\U0001F1ED\U0001F1F7',
        'CU': '\U0001F1E8\U0001F1FA',
        'CY': '\U0001F1E8\U0001F1FE',
        'CZ': '\U0001F1E8\U0001F1FF',
        'CD': '\U0001F1E8\U0001F1E9',
        'DK': '\U0001F1E9\U0001F1F0',
        'DJ': '\U0001F1E9\U0001F1EF',
        'DM': '\U0001F1E9\U0001F1F2',
        'DO': '\U0001F1E9\U0001F1F4',
        'TL': '\U0001F1F9\U0001F1F1',
        'EC': '\U0001F1EA\U0001F1E8',
        'EG': '\U0001F1EA\U0001F1EC',
        'SV': '\U0001F1F8\U0001F1FB',
        'GQ': '\U0001F1EC\U0001F1F6',
        'ER': '\U0001F1EA\U0001F1F7',
        'EE': '\U0001F1EA\U0001F1EA',
        'ET': '\U0001F1EA\U0001F1F9',
        'FJ': '\U0001F1EB\U0001F1EF',
        'FI': '\U0001F1EB\U0001F1EE',
        'FR': '\U0001F1EB\U0001F1F7',
        'GA': '\U0001F1EC\U0001F1E6',
        'GM': '\U0001F1EC\U0001F1F2',
        'GE': '\U0001F1EC\U0001F1EA',
        'DE': '\U0001F1E9\U0001F1EA',
        'GH': '\U0001F1EC\U0001F1ED',
        'GR': '\U0001F1EC\U0001F1F7',
        'GD': '\U0001F1EC\U0001F1E9',
        'GT': '\U0001F1EC\U0001F1F9',
        'GN': '\U0001F1EC\U0001F1F3',
        'GW': '\U0001F1EC\U0001F1FC',
        'GY': '\U0001F1EC\U0001F1FE',
        'HT': '\U0001F1ED\U0001F1F9',
        'HN': '\U0001F1ED\U0001F1F3',
        'HU': '\U0001F1ED\U0001F1FA',
        'HK': '\U0001F1ED\U0001F1F0',
        'IS': '\U0001F1EE\U0001F1F8',
        'IN': '\U0001F1EE\U0001F1F3',
        'ID': '\U0001F1EE\U0001F1E9',
        'IR': '\U0001F1EE\U0001F1F7',
        'IQ': '\U0001F1EE\U0001F1F6',
        'IE': '\U0001F1EE\U0001F1EA',
        'IL': '\U0001F1EE\U0001F1F1',
        'IT': '\U0001F1EE\U0001F1F9',
        'JM': '\U0001F1EF\U0001F1F2',
        'JP': '\U0001F1EF\U0001F1F5',
        'JO': '\U0001F1EF\U0001F1F4',
        'KZ': '\U0001F1F0\U0001F1FF',
        'KE': '\U0001F1F0\U0001F1EA',
        'KI': '\U0001F1F0\U0001F1EE',
        'KP': '\U0001F1F0\U0001F1F5',
        'KR': '\U0001F1F0\U0001F1F7',
        'KW': '\U0001F1F0\U0001F1FC',
        'KG': '\U0001F1F0\U0001F1EC',
        'LA': '\U0001F1F1\U0001F1E6',
        'LV': '\U0001F1F1\U0001F1FB',
        'LB': '\U0001F1F1\U0001F1E7',
        'LS': '\U0001F1F1\U0001F1F8',
        'LR': '\U0001F1F1\U0001F1F7',
        'LY': '\U0001F1F1\U0001F1FE',
        'LI': '\U0001F1F1\U0001F1EE',
        'LT': '\U0001F1F1\U0001F1F9',
        'LU': '\U0001F1F1\U0001F1FA',
        'MK': '\U0001F1F2\U0001F1F0',
        'MG': '\U0001F1F2\U0001F1EC',
        'MW': '\U0001F1F2\U0001F1FC',
        'MY': '\U0001F1F2\U0001F1FE',
        'MV': '\U0001F1F2\U0001F1FB',
        'ML': '\U0001F1F2\U0001F1F1',
        'MT': '\U0001F1F2\U0001F1F9',
        'MH': '\U0001F1F2\U0001F1ED',
        'MR': '\U0001F1F2\U0001F1F7',
        'MU': '\U0001F1F2\U0001F1FA',
        'MX': '\U0001F1F2\U0001F1FD',
        'FM': '\U0001F1EB\U0001F1F2',
        'MD': '\U0001F1F2\U0001F1E9',
        'MC': '\U0001F1F2\U0001F1E8',
        'MN': '\U0001F1F2\U0001F1F3',
        'ME': '\U0001F1F2\U0001F1EA',
        'MA': '\U0001F1F2\U0001F1E6',
        'MZ': '\U0001F1F2\U0001F1FF',
        'MM': '\U0001F1F2\U0001F1F2',
        'NA': '\U0001F1F3\U0001F1E6',
        'NR': '\U0001F1F3\U0001F1F7',
        'NP': '\U0001F1F3\U0001F1F5',
        'NL': '\U0001F1F3\U0001F1F1',
        'NZ': '\U0001F1F3\U0001F1FF',
        'NI': '\U0001F1F3\U0001F1EE',
        'NE': '\U0001F1F3\U0001F1EA',
        'NG': '\U0001F1F3\U0001F1EC',
        'NU': '\U0001F1F3\U0001F1FA',
        'NO': '\U0001F1F3\U0001F1F4',
        'OM': '\U0001F1F4\U0001F1F2',
        'PK': '\U0001F1F5\U0001F1F0',
        'PW': '\U0001F1F5\U0001F1FC',
        'PS': '\U0001F1F5\U0001F1F8',
        'PA': '\U0001F1F5\U0001F1E6',
        'PG': '\U0001F1F5\U0001F1EC',
        'PY': '\U0001F1F5\U0001F1FE',
        'PE': '\U0001F1F5\U0001F1EA',
        'PH': '\U0001F1F5\U0001F1ED',
        'PL': '\U0001F1F5\U0001F1F1',
        'PT': '\U0001F1F5\U0001F1F9',
        'QA': '\U0001F1F6\U0001F1E6',
        'RO': '\U0001F1F7\U0001F1F4',
        'RU': '\U0001F1F7\U0001F1FA',
        'RW': '\U0001F1F7\U0001F1FC',
        'KN': '\U0001F1F0\U0001F1F3',
        'LC': '\U0001F1F1\U0001F1E8',
        'VC': '\U0001F1FB\U0001F1E8',
        'WS': '\U0001F1FC\U0001F1F8',
        'SM': '\U0001F1F8\U0001F1F2',
        'ST': '\U0001F1F8\U0001F1F9',
        'SA': '\U0001F1F8\U0001F1E6',
        'SN': '\U0001F1F8\U0001F1F3',
        'RS': '\U0001F1F7\U0001F1F8',
        'SC': '\U0001F1F8\U0001F1E8',
        'SL': '\U0001F1F8\U0001F1F1',
        'SG': '\U0001F1F8\U0001F1EC',
        'SK': '\U0001F1F8\U0001F1F0',
        'SI': '\U0001F1F8\U0001F1EE',
        'SB': '\U0001F1F8\U0001F1E7',
        'SO': '\U0001F1F8\U0001F1F4',
        'ZA': '\U0001F1FF\U0001F1E6',
        'SS': '\U0001F1F8\U0001F1F8',
        'ES': '\U0001F1EA\U0001F1F8',
        'LK': '\U0001F1F1\U0001F1F0',
        'SD': '\U0001F1F8\U0001F1E9',
        'SR': '\U0001F1F8\U0001F1F7',
        'SZ': '\U0001F1F8\U0001F1FF',
        'SE': '\U0001F1F8\U0001F1EA',
        'CH': '\U0001F1E8\U0001F1ED',
        'SY': '\U0001F1F8\U0001F1FE',
        'TW': '\U0001F1F9\U0001F1FC',
        'TJ': '\U0001F1F9\U0001F1EF',
        'TZ': '\U0001F1F9\U0001F1FF',
        'TH': '\U0001F1F9\U0001F1ED',
        'TG': '\U0001F1F9\U0001F1EC',
        'TO': '\U0001F1F9\U0001F1F4',
        'TT': '\U0001F1F9\U0001F1F9',
        'TN': '\U0001F1F9\U0001F1F3',
        'TR': '\U0001F1F9\U0001F1F7',
        'TM': '\U0001F1F9\U0001F1F2',
        'TV': '\U0001F1F9\U0001F1FB',
        'UG': '\U0001F1FA\U0001F1EC',
        'UA': '\U0001F1FA\U0001F1E6',
        'AE': '\U0001F1E6\U0001F1EA',
        'GB': '\U0001F1EC\U0001F1E7',
        'US': '\U0001F1FA\U0001F1F8',
        'UY': '\U0001F1FA\U0001F1FE',
        'UZ': '\U0001F1FA\U0001F1FF',
        'VU': '\U0001F1FB\U0001F1FA',
        'VA': '\U0001F1FB\U0001F1E6',
        'VE': '\U0001F1FB\U0001F1EA',
        'VN': '\U0001F1FB\U0001F1F3',
        'YE': '\U0001F1FE\U0001F1EA',
        'ZM': '\U0001F1FF\U0001F1F2',
        'ZW': '\U0001F1FF\U0001F1FC',
    }

    return country_flags.get(country_code, '')
