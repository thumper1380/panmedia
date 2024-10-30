from apps.utils.serializers import DetailSerializer, StatusField, ListSerializer
from apps.users.serializers import UserWriteWOPasswordSerializer
from django_countries.serializer_fields import CountryField
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from .models import Postback, Affiliate, IPWhitelist, Pixel


class IPWhitelistSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPWhitelist
        fields = ('ip_address',)
        depth = 1


class PostbackSerializer(serializers.ModelSerializer):  # TODO add depth
    class Meta:
        model = Postback
        fields = '__all__'
        depth = 1


class PixelSerializer(serializers.ModelSerializer):
    # type = serializers.CharField(source='get_type_display')
    class Meta:
        model = Pixel
        fields = ['type', 'content']
        depth = 1


class AffiliateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affiliate
        fields = '__all__'
        depth = 1


class AffiliateCreateSerializer(serializers.ModelSerializer):
    # User fields
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)

    # Affiliate fields
    company_name = serializers.CharField()
    country = serializers.CharField()
    telegram = serializers.CharField()
    skype = serializers.CharField()

    class Meta:
        model = Affiliate
        fields = ['company_name', 'email', 'first_name',
                  'last_name', 'country', 'telegram', 'skype']

    def create(self, validated_data):
        # Extract user data
        user_data = {
            'email': validated_data.pop('email'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
        }

        # Create user
        user = UserWriteWOPasswordSerializer.create(
            UserWriteWOPasswordSerializer(), validated_data=user_data)

        # Create affiliate with the remaining data and link to the user
        affiliate = Affiliate.objects.create(user=user, **validated_data)

        return affiliate


class PanmediaResponseSerializer(serializers.Serializer):
    """ This is a sample serializer for showing my intent"""
    success = serializers.BooleanField(
        help_text="Whether the request was successful or not.",
    )


class ErrorResponseSerializer(PanmediaResponseSerializer):
    """ This is a sample serializer for showing my intent"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, many=False)
        self.fields['message'] = serializers.CharField(
            help_text="The error message returned by the request."
        )
        self.fields['success'].default = False


class SuccessResponseSerializer(PanmediaResponseSerializer):
    """ This is a sample serializer for showing my intent"""

    def __init__(self, *args, other_serializer, **kwargs):
        super().__init__(*args, **kwargs, many=False)
        self.fields['data'] = other_serializer(
            help_text="The data returned by the request.",
        )
        self.fields['success'].default = True


class LeadResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    auto_login_url = serializers.CharField()
    thank_you_url = serializers.CharField()
    pixel = serializers.ListField(
        child=PixelSerializer()
    )


class AffiliateDetailSerializer(ListSerializer):
    # id = serializers.IntegerField(read_only=True)
    country = CountryField()
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    is_active = StatusField(read_only=True, label='Status')

    class Meta:
        model = Affiliate
        # fields = ['id', 'company_name', 'country', 'telegram', 'skype']
        fields = ['id', 'first_name', 'last_name', 'email',
                  'company_name', 'is_active', 'country', 'telegram', 'skype']

    def update(self, instance, validated_data):
        # Handle nested user data
        user_data = validated_data.pop('user', {})
        user = instance.user

        # Update user
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.email = user_data.get('email', user.email)

        user.save()

        # Update affiliate
        instance.company_name = validated_data.get(
            'company_name', instance.company_name)
        instance.country = validated_data.get('country', instance.country)
        instance.telegram = validated_data.get('telegram', instance.telegram)
        instance.skype = validated_data.get('skype', instance.skype)
        instance.save()

        return instance
