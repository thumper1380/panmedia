from typing import Any, Callable, Dict, Optional, Union
from typing import Any, Dict, List, Optional
from uuid import UUID
from langchain.callbacks.base import BaseCallbackHandler
# from langchain.callbacks import ArizeCallbackHandler
from langchain_core.outputs import ChatGenerationChunk, GenerationChunk, LLMResult
from .models import Conversation, Message
from langchain.callbacks import FileCallbackHandler

# import telegram message
from telegram import Update, ChatAction

from django.utils import timezone
import random


class DjangoCallbackHandler(BaseCallbackHandler):
    """Callback handler for Django."""
    def __init__(self, conversation: Conversation, update: Update):
        self.conversation = conversation
        self.update = update
        self.tg_msg = None
        self.message = ''
        self.start_time = timezone.now()

    # def on_llm_start(
    #     self,
    #     serialized: Dict[str, Any],
    #     prompts: List[str],
    #     *,
    #     run_id: UUID,
    #     parent_run_id: Optional[UUID] = None,
    #     tags: Optional[List[str]] = None,
    #     metadata: Optional[Dict[str, Any]] = None,
    #     **kwargs: Any,
    # ) -> Any:
    #     """Run when LLM starts running."""
    #     self.tg_msg = self.update.message.reply_text(
    #         "Thinking", parse_mode='Markdown')

    #     self.update.message.chat.send_action(action=ChatAction.TYPING)


    # def on_llm_new_token(
    #     self,
    #     token: str,
    #     *,
    #     chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]] = None,
    #     run_id: UUID,
    #     parent_run_id: Optional[UUID] = None,
    #     **kwargs: Any,
    # ) -> Any:
    #     # keep last message and add new token to the telegram message edit it
    #     # how to send typing action? self.update.message.chat.send_action(action=ChatAction.TYPING)

    #     # create animation Thinking..., Thinking.., Thinking., Thinking.., Thinking...

    #     if self.tg_msg and random.random() < 0.7:
    #         self.tg_msg.edit_text(
    #             text="Thinking" + "." * (timezone.now().second % 5), parse_mode='Markdown')
            
        


    #     # self.message += token
    #     # if self.tg_msg:
    #     #     # randomally decide if we want to edit the message  because tg rate limit
    #     #     if self.tg_msg and random.random() < 0.25:
    #     #         self.tg_msg.edit_text(text=self.message, parse_mode='Markdown')
    #     #     # self.tg_msg.edit_text(text=self.message, parse_mode='Markdown')
        

    # def on_llm_end(
    #     self,
    #     response: LLMResult,
    #     *,
    #     run_id: UUID,
    #     parent_run_id: Optional[UUID] = None,
    #     **kwargs: Any,
    # ) -> Any:
    #     """Run when LLM ends running."""
    #     # self.tg_msg.delete()
    #     # self.tg_msg.delete()
    #     # print(response.generations[0][0].message.content)
    #     # self.tg_msg = self.tg_msg.edit_text(
    #     #     text=response.generations[0][0].message.content, parse_mode='Markdown')
    #     if self.tg_msg:
    #         self.tg_msg.delete()



    def on_tool_end(
        self,
        output: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when tool ends running."""
        if output:
            tool_name = kwargs.get('name')
            self.conversation.messages.create(
                content=output,
                name=tool_name,
                role=Message.RoleChoices.FUNCTION_RESPONSE
            )
