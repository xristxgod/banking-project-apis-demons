from telebot import types

from django.db import transaction
from django.utils.translation import gettext as _

from apps.telegram.bot import bot
from apps.telegram.bot_apps.orders import keyboards


class DepositSteps:
    class Step:
        def __init__(self):
            self.network_id = None
            self.currency_id = None

    def __init__(self):
        self.storage = {}

    def new(self, chat_id: int):
        self.storage[chat_id] = self.Step()
        return self.get(chat_id)

    def get(self, chat_id: int):
        return self.storage[chat_id]


def deposit(msg_or_cq: types.Message | types.CallbackQuery, data: dict):
    user = data['user']
    text = _('Take network!')
    markup = keyboards.get_network_keyboard()

    if isinstance(msg_or_cq, types.Message):
        bot.send_message(
            chat_id=user.chat_id,
            text=text,
            reply_markup=markup,
        )
    else:
        bot.edit_message_text(
            chat_id=user.chat_id,
            text=text,
            message_id=msg_or_cq.message.message_id,
            reply_markup=markup,
        )

    # TODO
    bot.register_next_step_handler(

    )
