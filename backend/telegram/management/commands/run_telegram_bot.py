from django.core.management.base import BaseCommand

from telegram.bot import bot


class Command(BaseCommand):
    help = 'Implemented to Django application telegram bot setup command'

    def handle(self, *args, **options):
        bot.infinity_polling()
