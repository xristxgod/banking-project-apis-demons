from django.core.management.base import BaseCommand

# from telegram.bot import main_bot as bot


class Command(BaseCommand):
    help = 'Implemented to Django application telegram bot setup command'

    def handle(self, *args, **options):
        print('t')
        # bot.infinity_polling()
