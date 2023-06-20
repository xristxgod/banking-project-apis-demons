from telebot import types

from django.db import transaction
from django.utils.translation import gettext as _

import settings
from old_apps.telegram.views import bot
from old_apps.telegram.bot_apps.orders import callbacks
from old_apps.cryptocurrencies.models import Network, Currency

from old_apps.orders.services import create_order, get_payment_receipt_url

# TODO добавть хранилище для шагов


def select_network_handler(cq: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()

    for network in Network.objects.all():
        markup.row(types.InlineKeyboardButton(
            text=network.name,
            callback_data=callbacks.select_network.new(network.pk)
        ))

    bot.edit_message_text(
        text=_('Select network'),
        reply_markup=markup,
        message_id=cq.message.message_id,
    )


def select_currency_handler(cq: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()

    for currency in Currency.objects.filter(network_id=''):
        markup.row(types.InlineKeyboardButton(
            text=currency.verbose_telegram_name,
            callback_data=callbacks.select_currency.new(currency.pk),
        ))

    bot.edit_message_text(
        text=_('Select Currency'),
        reply_markup=markup,
        message_id=cq.message.message_id,
    )


def write_amount_handler(cq: types.CallbackQuery):
    pass


def create_order_handler(message: types.Message, user):
    order = create_order(
        user=user,
        amount='',
        currency='',
        message_id=message.message_id,
    )

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(
            text=_('To pay!'),
            url=get_payment_receipt_url(order),
        )
    )
    markup.row(
        types.InlineKeyboardButton(
            text=_('Cancel'),
            callback_data=''
        )
    )

    bot.send_message(
        text=_(f'Order #: {order.pk} successfully created!'),

    )


def cancel_order(cq: types.CallbackQuery):
    pass
