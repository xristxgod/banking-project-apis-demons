import abc
from typing import Optional

import telebot
from telebot import types

from apps.telegram.bot_apps.middlewares import UserData


class AbstractHandler(metaclass=abc.ABCMeta):

    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot
        self.registration_handlers()

    def __call__(self, msg_or_cq: types.Message | types.CallbackQuery, data: dict):
        from_user = msg_or_cq.from_user

        if isinstance(msg_or_cq, types.Message):
            message_id, cb_data, message = None, None, msg_or_cq
        else:
            message_id, cb_data, message = msg_or_cq.message.message_id, msg_or_cq.data, msg_or_cq.message

        if self.has_auth and data['user'] is None:
            params = self.without_auth_call(message=message, from_user=from_user, cb_data=cb_data)
        else:
            params = self.call(message=message, user=data['user'], cb_data=cb_data)

        self.notify(
            chat_id=from_user.id,
            message_id=message_id,
            **params,
        )

    def notify(self, chat_id: int, message_id: Optional[int] = None, **params):
        if message_id:
            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                **params,
            )
        else:
            self.bot.send_message(
                chat_id=chat_id,
                **params,
            )

    @property
    def has_auth(self) -> bool:
        return True

    @abc.abstractmethod
    def registration_handlers(self): ...

    @abc.abstractmethod
    def call(self, message: types.Message, user: UserData, cb_data: str) -> dict: ...

    @abc.abstractmethod
    def without_auth_call(self, message: types.Message, from_user: types.User, cb_data: str) -> dict: ...
