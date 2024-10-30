from django.utils.text import slugify
from apps.settings.serializers import create_form_serializer, create_serializer_field
from rest_framework import serializers
from apps.trafficdata.models import TrafficData, Source
from drf_spectacular.extensions import OpenApiSerializerFieldExtension


class LeadRequestSerializerView(serializers.Serializer):
    # add description for each field
    ip = serializers.IPAddressField(
        required=False, help_text="Will take the IP from the request if not provided", source='ip_address')
    country = serializers.CharField(
        help_text="ISO 3166-1 alpha-2 country code", required=False, max_length=2)
    source = serializers.IntegerField(
        help_text="The ID of the source", required=False, source='source.id')
    # optional fields
    language = serializers.CharField(
        required=False, help_text="ISO 639-1 2-letter language code", max_length=2)
    aff_sub_1 = serializers.CharField(required=False)
    aff_sub_2 = serializers.CharField(required=False)
    aff_sub_3 = serializers.CharField(required=False)
    aff_sub_4 = serializers.CharField(required=False)
    aff_sub_5 = serializers.CharField(required=False)


def create_dynamic_lead_request_serializer(form):
    # Creates a dynamic serializer class according to the form fields
    DynamicFormSerializer = create_form_serializer(form)

    # Get the fields from the static serializer
    static_fields = LeadRequestSerializerView().get_fields()

    # Get the fields from the dynamic serializer
    dynamic_fields = {field.key: create_serializer_field(
        field) for field in form.fields.all()}

    # Combine the fields from both serializers
    # Split the static fields into two parts: before and after 'aff_sub_1'
    static_fields_before = {k: static_fields[k] for k in list(static_fields.keys())[:list(static_fields.keys()).index('aff_sub_1')]}
    static_fields_after = {k: static_fields[k] for k in list(static_fields.keys())[list(static_fields.keys()).index('aff_sub_1'):]}

    combined_fields = {**static_fields_before, **dynamic_fields, **static_fields_after}

    # Create the Meta class with combined fields
    Meta = type('Meta', (), {'model': TrafficData,
                'fields': list(combined_fields.keys())})

    # Create the combined serializer class
    class_name = f"{slugify(form.name).replace('-', '_').capitalize()}Serializer"
    serializer_class = type(class_name, (DynamicFormSerializer,), {
                            'Meta': Meta, **combined_fields})
    return serializer_class


class LeadRequestSerializer(serializers.Serializer):
    # add description for each field
    ip = serializers.IPAddressField(
        required=False, help_text="Will take the IP from the request if not provided", source='ip_address')
    country = serializers.CharField(
        help_text="ISO 3166-1 alpha-2 country code", required=False, max_length=2)
    source = serializers.IntegerField(
        help_text="The ID of the source", required=False, source='source.id')
    # optional fields
    language = serializers.CharField(
        required=False, help_text="ISO 639-1 2-letter language code", max_length=2)
    aff_sub_1 = serializers.CharField(required=False)
    aff_sub_2 = serializers.CharField(required=False)
    aff_sub_3 = serializers.CharField(required=False)
    aff_sub_4 = serializers.CharField(required=False)
    aff_sub_5 = serializers.CharField(required=False)
    aff_sub_6 = serializers.CharField(required=False)
    aff_sub_7 = serializers.CharField(required=False)
    aff_sub_8 = serializers.CharField(required=False)
    aff_sub_9 = serializers.CharField(required=False)
    aff_sub_10 = serializers.CharField(required=False)
    aff_sub_11 = serializers.CharField(required=False)
    aff_sub_12 = serializers.CharField(required=False)
    aff_sub_13 = serializers.CharField(required=False)
    aff_sub_14 = serializers.CharField(required=False)
    aff_sub_15 = serializers.CharField(required=False)
    aff_sub_16 = serializers.CharField(required=False)
    aff_sub_17 = serializers.CharField(required=False)
    aff_sub_18 = serializers.CharField(required=False)
    aff_sub_19 = serializers.CharField(required=False)
    aff_sub_20 = serializers.CharField(required=False)

    def create(self, validated_data):

        # Add the affiliate to the validated data
        validated_data['affiliate'] = self.context['affiliate']
        validated_data['funnel'] = self.context['funnel']

        source = None
        if 'source' in validated_data:
            # get 'id' from 'source' dictionary
            source_id = validated_data.pop('source')['id']
            try:
                source = Source.objects.get(id=source_id)
            except Source.DoesNotExist:
                pass

        validated_data['source'] = source

        lead = TrafficData.objects.create(**validated_data)

        lead.save()
        return lead


class AffiliateSalesSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    class Meta:
        model = TrafficData
        fields = ('id', 'email',)

    def get_email(self, obj):
        return obj.profile.get('email')


class AffiliateLeadsSerializer(serializers.ModelSerializer):
    sale_status = serializers.SerializerMethodField()
    has_conversion = serializers.SerializerMethodField()
    conversion_date = serializers.SerializerMethodField()
    country = serializers.CharField(source='country.code')
    created_at = serializers.CharField()

    def __init__(self, *args, **kwargs):
        context = kwargs.get('context', {})
        self.can_see_real_status = context.get('can_see_real_status', False)
        self.can_see_lead_info = context.get('can_see_lead_info', False)

        super().__init__(*args, **kwargs)

        if self.can_see_lead_info:
            self.fields['email'] = serializers.CharField(
                source='profile.email')

    class Meta:
        model = TrafficData
        fields = ('id', 'country', 'aff_sub_1', 'aff_sub_2', 'aff_sub_3', 'aff_sub_4',
                  'aff_sub_5', 'sale_status', 'has_conversion', 'conversion_date', 'created_at')

    def get_sale_status(self, obj):
        if self.can_see_real_status:
            return obj.advertiser_sale_status
        return obj.afm_status

    def get_has_conversion(self, obj) -> bool:
        return False

    def get_conversion_date(self, obj) -> str:
        return obj.conversions.first().created_at if obj.conversions.first() else None

    def created_at(self, obj):
        return obj.created_at

    def get_country_code(self, obj):
        return obj.country.code
