from .models import Conversation, Message, ConversationSummary
from typing import List, Any, Dict
from langchain.memory import ConversationSummaryBufferMemory
from langchain.schema.messages import FunctionMessage, BaseMessage


class DjangoConversationBufferMemory(ConversationSummaryBufferMemory):
    conversation: Conversation

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save the conversation history to the database."""
        input_str, output_str = self._get_input_output(inputs, outputs)

        # self.chat_memory.add_user_message(input_str)
        # self.chat_memory.add_ai_message(output_str)


        self.conversation.messages.create(
            content=output_str, role=Message.RoleChoices.ASSISTANT)

        self.update_summary()

    def update_summary(self):
        """Update the conversation summary"""
        conversation = self.conversation
        summary = ConversationSummary.objects.filter(
            conversation=conversation).first()
        if summary:
            self.moving_summary_buffer = summary.content or ""

    def load_memory_from_db(self):
        messages = self.conversation.messages.order_by(
            'created_at').filter(summarized_at__isnull=True)

        for message in messages:
            if message.role == Message.RoleChoices.USER:
                self.chat_memory.add_user_message(message.content)
            elif message.role == Message.RoleChoices.ASSISTANT:
                self.chat_memory.add_ai_message(message.content)
            elif message.role == Message.RoleChoices.FUNCTION_RESPONSE:
                self.chat_memory.add_message(FunctionMessage(
                    name=Message.RoleChoices.FUNCTION_RESPONSE, content=message.content))

        self.update_summary()

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Override the parent method to also load from DB."""
        self.load_memory_from_db()
        return super().load_memory_variables(inputs)
