# tasks.py
# here we will define task that will summarize conversation history
# and save it to the database
from django.utils import timezone
from typing import Any, Dict, List
from langchain_core.messages import BaseMessage, SystemMessage, get_buffer_string, HumanMessage, AIMessage, FunctionMessage

from langchain_core.messages import BaseMessage, get_buffer_string
from langchain.memory.prompt import SUMMARY_PROMPT
from langchain.chains.llm import LLMChain
from celery import shared_task
from .models import Conversation, ConversationSummary, Message, MessageQuerySet
# import chatopenai
from langchain.chat_models import ChatOpenAI
from django.conf import settings


def format_messages_for_summary(messages: MessageQuerySet) -> List[BaseMessage]:
    """Format messages from the database for summarization."""
    formatted_messages = []
    for message in messages:
        # Format each message based on its role
        if message.role == Message.RoleChoices.USER:
            formatted_messages.append(HumanMessage(content=message.content))
        elif message.role == Message.RoleChoices.ASSISTANT:
            formatted_messages.append(AIMessage(content=message.content))
        elif message.role == Message.RoleChoices.FUNCTION_RESPONSE:
            formatted_messages.append(FunctionMessage(
                name=Message.RoleChoices.FUNCTION_RESPONSE, content=message.content))
        elif message.role == Message.RoleChoices.SYSTEM:
            formatted_messages.append(SystemMessage(content=message.content))

    return formatted_messages


@shared_task
def summarize(conversation_id: str) -> None:
    """Summarize the conversation and save it to the database."""
    conversation = Conversation.objects.get(id=conversation_id)

    # get all messages that are not summarized yet
    messages = conversation.messages.order_by(
        '-created_at').filter(summarized_at__isnull=True)
    # exclude last 10 messages
    if len(messages) <= 10:
        return 'Not enough messages to summarize.'

    messages = messages[10:]  # exclude last 10 messages

    formatted_messages = format_messages_for_summary(messages)
    messages_buffer = get_buffer_string(
        human_prefix="Human", ai_prefix="AI", messages=formatted_messages)

    # Summarize the conversation
    GPT_MODEL = 'gpt-4-1106-preview'

    llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY,
                     model=GPT_MODEL)

    conversation_summary = ConversationSummary.objects.filter(
        conversation=conversation).first()

    summary_content = conversation_summary.content if conversation_summary else ''

    chain = LLMChain(llm=llm, prompt=SUMMARY_PROMPT)

    response = chain.predict(
        summary=summary_content, new_lines=messages_buffer)

    conversation.messages.filter(id__in=[message.id for message in messages]).update(
        summarized_at=timezone.now())

    # Save the summary to the database
    if conversation_summary:
        conversation_summary.set_content(response)
    else:
        ConversationSummary.objects.create(
            conversation=conversation, content=response)

    return response


@shared_task
def summarize_conversations() -> str:
    """Summarize all conversations."""
    conversations = Conversation.objects.all()
    for conversation in conversations:
        summarize.delay(conversation.id)

    return 'Summarizing all conversations...'
