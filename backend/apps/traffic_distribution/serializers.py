from apps.utils.folders import CountryFolder, AffiliateFolder, AdvertiserFolder
from apps.utils.serializers import RelatedField
from django_countries.serializer_fields import CountryField
from .models import (RotationControlCountryFolder, RotationContolAffiliateFolder,
                     RotationControlAdvertiserFolder, RotationControlAffiliateSplitFolder,
                     RotationControlCountrySplitFolder, RotationControlAdvertiserSplit, CapFolder)
from apps.utils.folders import Folder
from .models import RotationControlCountryFolder
from apps.utils.serializers import DetailSerializer, ListSerializer
from rest_framework import serializers
from .models import GroupTemplate, SettingsTemplate, Provider, Advertiser, RotationControl

from rest_polymorphic.serializers import PolymorphicSerializer

from .models import RotationControlCountryFolder


class SettingsTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingsTemplate
        fields = ('name',)


class GroupTemplateSerializer(serializers.ModelSerializer):
    settings = SettingsTemplateSerializer(
        many=True, read_only=True, source='settingstemplate_set')

    class Meta:
        model = GroupTemplate
        fields = ('name', 'settings')


class ProviderSerializer(serializers.ModelSerializer):
    groups = GroupTemplateSerializer(
        many=True, read_only=True, source='grouptemplate_set')

    class Meta:
        model = Provider
        fields = ('name', 'groups')


class AdvertiserSerializer(serializers.ModelSerializer):
    # provider = ProviderSerializer()

    class Meta:
        model = Advertiser
        fields = ('id', 'name',)


class AdvertiserDetailSerializer(DetailSerializer):
    provider = serializers.CharField(source='provider.name')

    class Meta:
        model = Advertiser
        fields = ['id', 'name', 'active', 'is_test', 'provider', 'created_at']


# import django-countries model


class BaseFolderSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    parent_id = serializers.IntegerField()
    disabled = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    isLeaf = serializers.SerializerMethodField()

    def get_children(self, obj):
        children = obj.get_children()
        return ReadFolderPolymorphicSerializer(children, many=True).data if children else None

    def get_disabled(self, obj):
        return not obj.is_active

    def get_isLeaf(self, obj):
        return not obj.get_children().exists()


class CountryFolderSerializer(BaseFolderSerializer):
    countries = serializers.ListField(child=CountryField())


class AffiliateFolderSerializer(BaseFolderSerializer):
    affiliate = RelatedField(read_only=True, source='company_name')


class AdvertiserFolderSerializer(BaseFolderSerializer):
    advertiser = RelatedField(read_only=True, source='name')


class AffiliateSplitFolderSerializer(BaseFolderSerializer):
    affiliate = RelatedField(read_only=True, source='company_name')


class CountrySplitFolderSerializer(BaseFolderSerializer):
    countries = serializers.ListField(child=CountryField())


class AdvertiserSplitFolderSerializer(BaseFolderSerializer):
    advertiser = RelatedField(read_only=True, source='name')

    # cap_amount = models.PositiveIntegerField(default=1000)
    # current_amount = models.PositiveIntegerField(default=0)
    # cap_type = models.CharField(
    #     max_length=255, choices=TypeChoices.choices, default=TypeChoices.REGULAR)


class CapFolderSerializer(BaseFolderSerializer):
    cap_amount = serializers.IntegerField()
    current_amount = serializers.IntegerField()
    cap_type = serializers.CharField()


class ReadFolderPolymorphicSerializer(PolymorphicSerializer):
    resource_type_field_name = 'type'
    model_serializer_mapping = {
        RotationControlCountryFolder: CountryFolderSerializer,
        AffiliateFolder: AffiliateFolderSerializer,
        AdvertiserFolder: AdvertiserFolderSerializer,
        RotationControlAffiliateSplitFolder: AffiliateSplitFolderSerializer,
        RotationControlCountrySplitFolder: CountrySplitFolderSerializer,
        RotationControlAdvertiserSplit: AdvertiserSplitFolderSerializer,
        CapFolder: CapFolderSerializer
    }


class CreateCountryFolderSerializer(serializers.ModelSerializer):
    countries = serializers.ListField(child=CountryField())

    class Meta:
        model = RotationControlCountryFolder
        fields = ('name', 'countries', 'parent')


class WriteFolderPolymorphicSerializer(ReadFolderPolymorphicSerializer):
    model_serializer_mapping = {
        RotationControlCountryFolder: CreateCountryFolderSerializer,
    }
