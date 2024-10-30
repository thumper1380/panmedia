# serializers.py


from .models import WebauthnCredentials, WebauthnRegistration
from rest_framework import serializers


class WebauthnCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebauthnCredentials
        fields = "__all__"


class WebauthnRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = WebauthnRegistration
        fields = "__all__"

    def create(self, validated_data):
        return WebauthnRegistration.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.challenge = validated_data.get(
            "challenge", instance.challenge)
        instance.save()
        return instance
