from langchain_core.messages import AIMessage, HumanMessage
from asgiref.sync import sync_to_async
from django.utils.translation import gettext_lazy as _
from datetime import datetime, time
from enum import Enum
from django.db import models

# Create your models here.

import requests
from django.conf import settings
# import openai
from openai import OpenAI
# import user model

from django.utils import timezone
import json
from django.core.serializers.json import DjangoJSONEncoder
from apps.settings.models import GoalType
from apps.traffic_distribution.models import Advertiser


class MessageQuerySet(models.QuerySet):
    ...


class Message(models.Model):
    """
    This model stores the messages that the chatbot will send to the user.
    """
    class RoleChoices(models.TextChoices):
        USER = 'user', _('User')
        SYSTEM = 'system', _('System')
        ASSISTANT = 'assistant', _('Assistant')
        FUNCTION_RESPONSE = 'function', _('Function')

    content = models.TextField()
    conversation = models.ForeignKey(
        'Conversation', on_delete=models.CASCADE, related_name='messages')
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(
        max_length=50, choices=RoleChoices.choices, default=RoleChoices.USER)
    summarized_at = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)

    objects = MessageQuerySet.as_manager()

    def __str__(self):
        return f'{self.role} - {self.content}'

    class Meta:
        verbose_name_plural = 'Messages'


class ConversationSummary(models.Model):

    """
    This model stores the summary of the conversation between the user and the chatbot.
    """
    conversation = models.OneToOneField(
        'Conversation', on_delete=models.CASCADE, related_name='summary')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.conversation} - {self.created_at}'

    class Meta:
        verbose_name_plural = 'Conversation Summaries'
        ordering = ['-created_at']

    def set_content(self, content: str):
        """
        This method will set the content of the summary.
        """
        self.content = content
        self.save()


class ConversationQuerySet(models.QuerySet):
    ...


class Conversation(models.Model):
    """
    This model stores the conversation between the user and the chatbot.
    """
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ConversationQuerySet.as_manager()

    def __str__(self):
        return f'{self.user.email} - {self.created_at}'

    class Meta:
        verbose_name_plural = 'Conversations'
        ordering = ['-created_at']

    def get_conversation(self) -> list:
        from .serializers import MessageSerializer as M
        messages = self.messages.all()
        serializer = M(messages, many=True)
        return json.loads(json.dumps(serializer.data, cls=DjangoJSONEncoder))

    def get_chat_history(self) -> list:
        """
        This method will return the chat history. in format of langchain_core.messages.AIMessage and langchain_core.messages.HumanMessage
        """
        chat_history = []
        for message in self.messages.all():
            if message.role == Message.RoleChoices.USER:
                chat_history.append(HumanMessage(content=message.content))
            elif message.role == Message.RoleChoices.ASSISTANT:
                chat_history.append(AIMessage(content=message.content))
        return chat_history

    def clear(self):
        """
        Clears the conversation between the user and the chatbot.
        """
        self.messages.all().delete()
        if hasattr(self, 'summary'):
            self.summary.delete()
