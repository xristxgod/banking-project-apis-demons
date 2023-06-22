from telebot import types

from django.utils.translation import gettext as _

from apps.telegram.bot_apps.orders import callbacks
from apps.cryptocurrencies.models import Network, Currency


def get_network_keyboard():
    markup = types.InlineKeyboardMarkup()

    for network in Network.objects.all():
        markup.row(types.InlineKeyboardButton(
            text=network.telegram_view,
            callback_data=callbacks.network.new(id=network.pk),
        ))

    return markup
