from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    content = serializers.CharField(source='message')

    class Meta:
        model = Message
        fields = ['role', 'content',]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # add name to message if role = function
        if ret['role'] == 'function':
            ret['name'] = instance.name

        return ret


