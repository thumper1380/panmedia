from rest_framework import serializers
from apps.trafficdata.models import TrafficData


class ClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficData
        fields = ['funnel', 'ip_address', 'user_agent', 'referrer', 'affiliate_id', 'os', 'os_version', 'source_id', 'browser', 'browser_version', 'device_model',
                  'device_type', 'x_requested_with', 'country', 'city', 'region', 'language', 'bot', 'latitude', 'longitude'] + [f'aff_sub_{i}' for i in range(1, 21)]

    def create(self, validated_data):
        return TrafficData.objects.create(**validated_data)
