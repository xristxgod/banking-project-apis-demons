from typing import Optional

from telebot import types

from django.db import transaction
from django.utils.translation import gettext as _

from old_apps.telegram.views import bot
from old_apps.telegram.models import User
from old_apps.telegram.bot_apps.start import callbacks
from old_apps.orders.services import orders_to_excel


def start_handler(message: types.Message, user: Optional[User] = None):
    if not user:
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(
            text=_('Registration'),
            callback_data=callbacks.registration
        ))

        bot.send_message(
            text=_('Pls registration!'),
            reply_markup=markup,
        )
    else:
        pass


@transaction.atomic()
def registration_handler(cq: types.CallbackQuery):
    user = User.objects.create(
        id=cq.from_user.id,
        username=cq.from_user.username,
    )
    bot.edit_message_text(
        text=_('Success'),
        message_id=cq.message.message_id,
    )


def menu_handler(cq: types.CallbackQuery, user: User):
    markup = types.InlineKeyboardMarkup()

    markup.row(types.InlineKeyboardButton(
        text=_('Orders'),
        callback_data='list_orders',
    ))

    markup.row(types.InlineKeyboardButton(
        text=_('Change language'),
        callback_data='change_language'
    ))

    markup.row(types.InlineKeyboardButton(
        text=_('Balance'),
        callback_data='balance',
    ))

    markup.row(types.InlineKeyboardButton(
        text=_('Deposit'),
        callback_data='deposit',
    ))

    markup.row(types.InlineKeyboardButton(
        text=_('Withdraw'),
        callback_data='withdraw',
    ))

    bot.edit_message_text(
        text=_('Menu'),
        reply_markup=markup,
        message_id=cq.message.message_id,
    )


def balance_handler(cb: types.CallbackQuery, user: User):
    balance_usd = user.balance.verbose_telegram_amount

    bot.send_message(
        text=_(f'Your balance: {balance_usd}'),
    )


def orders_handlers(cb: types.CallbackQuery, user: User):
    orders = user.orders.all()

    text = _('Orders:\n')
    for order in orders:
        pass

    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(
        text=_('To excel'),
        callback_data=orders_to_excel()
    ))

    bot.send_message(
        text=text,
        reply_markup=markup,
    )
