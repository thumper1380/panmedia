from django.core.management.base import BaseCommand
from django.conf import settings
from apps.telegrambot.bot import main

class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(rf'Running Telegram bot...'))
        main(token=settings.TELEGRAM_API_KEY)