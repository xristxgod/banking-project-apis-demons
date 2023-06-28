import re
import abc
from typing import Optional

import telebot
from telebot import types
from telebot.types import Message, CallbackQuery

from apps.telegram.middlewares.user import BaseUserData


class AbstractHandler(metaclass=abc.ABCMeta):
    reg_text_pattern: str = ''

    use_auth = True
    use_text_params = False

    @classmethod
    def _has_text_params(cls, call: Message | CallbackQuery):
        return isinstance(call, Message) and len(call.text.split())

    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot
        self.compile = re.compile(self.reg_text_pattern)
        self.registration_handlers()

    @abc.abstractmethod
    def registration_handlers(self): ...

    def _is_correct_pattern(self, text_params: Optional[str] = None) -> bool:
        return (
                text_params and
                self.compile.match(text_params) is not None
        )

    def _pre_call(self, message: Message, user: BaseUserData, **kwargs) -> dict:
        if self.use_auth and user.is_anonymous:
            return self.call_without_auth(message, user, kwargs['cb_data'])
        elif self.use_text_params and self._is_correct_pattern(kwargs['text_params']):
            return self.call_with_text_params(message, user, kwargs['text_params'])
        else:
            return self.call(message, user, kwargs['cb_data'])

    def __call__(self, call: Message | CallbackQuery, data: dict):
        message, cb_data, message_id = getattr(call, 'message', call), getattr(call, 'data', None), None
        if isinstance(call, CallbackQuery):
            message_id = message.message_id

        params = self._pre_call(
            message=message,
            user=data['user'],
            cb_data=cb_data,
            text_params=data.get('text_params'),
        )

        self.notify(
            chat_id=call.from_user.id,
            message_id=message_id,
            **params
        )

    @abc.abstractmethod
    def call_without_auth(self, message: types.Message, user: BaseUserData, cb_data: str) -> dict: ...

    @abc.abstractmethod
    def call(self, message: types.Message, user: BaseUserData, cb_data: str) -> dict: ...

    def call_with_text_params(self, message: types.Message, user: BaseUserData, text_params: str) -> dict: ...

    def notify(self, chat_id: int, message_id: Optional[int] = None, **params):
        if message_id or params.get('message_id'):
            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id or params.get('message_id'),
                parse_mode="Markdown",
                **params,
            )
        else:
            self.bot.send_message(
                chat_id=chat_id,
                parse_mode="Markdown",
                **params,
            )
