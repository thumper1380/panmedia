from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
import telegram
import asyncio

class Telegram:
    def __init__(self):
        self.telegram = telegram.Bot(token=settings.TELEGRAM_API_KEY)

    def send_message(self, chat_id, text, reply_to_message_id=None, parse_mode=None):
        self.telegram.send_message(chat_id=chat_id, text=text, reply_to_message_id=reply_to_message_id, parse_mode=parse_mode, disable_web_page_preview=True)

    def send_sticker(self, chat_id, sticker):
        self.telegram.send_sticker(chat_id=chat_id, sticker=sticker)


@api_view(['GET'])
def send_message(request):
    chat_id = request.query_params.get('chat_id')
    text = request.query_params.get('text')

    if chat_id and text:
        tg = Telegram()
        response = tg.send_message(chat_id, text)
        return Response(response)
    else:
        return Response({'error': 'Missing required parameters.'})
