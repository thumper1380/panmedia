from django.utils import timezone
from apps.affiliate.models import Affiliate
from apps.chatgpt.openai import OpenAI
from apps.affiliate.tools.toolkit import AffiliateToolKit
from telegram import ChatAction
from apps.chatgpt.models import Conversation
from apps.chatgpt.agent import initialize_agent
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging
from apps.chatgpt.callbacks import DjangoCallbackHandler
# Enable logging


# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO)
# logger = logging.getLogger(__name__)


# Define command handlers
from apps.chatgpt.models import Message


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi')


def chat_id(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        f'Your chat ID is: `{update.effective_chat.id}`', parse_mode='Markdown')


# import django timezone


def on_message(update: Update, context: CallbackContext) -> None:
    # send typing action
    is_group_chat = update.effective_chat.type == 'supergroup'

    if is_group_chat and update.message.reply_to_message != None:  # if it's general group
        # get repoly to message id
        # you are not allowed to reply in this group

        message = f"I can't reply to messages in this topic. You can send messages to me in general chat."

        context.bot.send_message(
            chat_id=update.effective_chat.id, text=message, reply_to_message_id=update.message.message_id, parse_mode='Markdown')
        return

    update.message.chat.send_action(action=ChatAction.RECORD_VIDEO)

    # get affiliate telegram profile by chat id
    try:
        affiliate: Affiliate = Affiliate.objects.get(
            telegram_profile__chat_id=update.effective_chat.id)
    except Affiliate.DoesNotExist:
        update.message.reply_text('You are not registered as affiliate.')
        return

    conversation, created = Conversation.objects.get_or_create(
        user=affiliate.user)
    

    toolkit = AffiliateToolKit(affiliate=affiliate, callbacks=[
                               DjangoCallbackHandler(conversation=conversation, update=update)])

    tools = toolkit.get_tools()

    first_name = update.message.from_user.first_name

    message_content = f'{first_name}: {update.message.text}'

    agent_executor = initialize_agent(
        conversation=conversation, update=update, tools=tools)

    is_client_first_message = conversation.messages.count() == 0

    conversation.messages.create(
        content=message_content, role=Message.RoleChoices.USER)
    if is_client_first_message:
        help_guide = agent_executor.invoke(
            {"input": f"Hey, this is {first_name}'s first message, please help him to get started.", }
        )
        update.message.reply_text(
            help_guide['output'], parse_mode='Markdown')

    else:

        agent_response = agent_executor.invoke(
            {
                "input": message_content,
            }
        )

        if agent_response:
            update.message.reply_text(
                agent_response['output'], parse_mode='Markdown')

    return


def on_voice_message(update: Update, context: CallbackContext) -> None:
    # send typing action
    update.message.chat.send_action(action=ChatAction.RECORD_AUDIO)

    voice_file = update.message.voice.get_file()

    openai = OpenAI()

    voice_file_text = openai.transcript(voice_file.download_as_bytearray())

    # set voice file text as message content
    update.message.text = voice_file_text

    on_message(update, context)


def main(token):
    # Create the Updater and pass it your bot's token
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register the command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("chat_id", chat_id))

    # on noncommand i.e message - send to agent executor
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, on_message))

    # handle voice messages
    dp.add_handler(MessageHandler(Filters.voice, on_voice_message))

    # Start the Bot
    updater.start_polling()
    updater.idle()
