import re
import abc
from typing import Optional

import telebot
from telebot import types
from telebot.types import Message, CallbackQuery

from apps.telegram.middlewares.user import BaseUserData


class AbstractHandler(metaclass=abc.ABCMeta):
    use_auth = True

    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot
        self.registration_handlers()
        self._subclass_init()

    @abc.abstractmethod
    def registration_handlers(self): ...

    @abc.abstractmethod
    def call_without_auth(self, message: Message, user: BaseUserData, extra: dict) -> dict: ...

    @abc.abstractmethod
    def call(self, message: Message, user: BaseUserData, extra: dict) -> dict: ...

    def _subclass_init(self):
        """Only subclasses"""

    def _get_subclass_params(self, message: Message, user: BaseUserData, extra: dict) -> Optional[dict]:
        """Only subclasses"""

    def _get_params(self, message: Message, user: BaseUserData, extra: dict) -> dict:
        if self.use_auth and user.is_anonymous:
            return self.call_without_auth(message, user, extra)

        if params := self._get_subclass_params(message, user, extra):
            return params

        return self.call(message, user, extra)

    def __call__(self, call: Message | CallbackQuery, data: dict):
        user = data['user']
        message = getattr(call, 'message', call)

        params = self._get_params(
            message=message,
            user=user,
            extra=dict(
                data=data,
                cb_data=getattr(call, 'data', ''),
            ),
        )

        message_id = params.get('message_id')
        if not message_id:
            message_id = message.message_id if isinstance(call, CallbackQuery) else None

        self.notify(
            user=user,
            message_id=message_id,
            **params,
        )

    def notify(self, user: BaseUserData, message_id: int, **params):
        if message_id:
            self.bot.edit_message_text(
                chat_id=user.chat_id,
                message_id=message_id or params.get('message_id'),
                parse_mode="Markdown",
                **params,
            )
        else:
            self.bot.send_message(
                chat_id=user.chat_id,
                parse_mode="Markdown",
                **params,
            )


class AbstractStepsMixin(abc.ABC):

    def _subclass_init(self):
        self.storage = {}

    def _get_subclass_params(self, message: Message, user: BaseUserData, extra: dict) -> Optional[dict]:
        if self.is_step(extra):
            return self.call_step(message, user, extra)
        return super()._get_subclass_params(message, user, extra)

    @abc.abstractmethod
    def is_step(self, extra: dict) -> bool: ...

    @abc.abstractmethod
    def call_step(self, message: Message, user: BaseUserData, extra: dict) -> dict: ...

    def notify(self, user: BaseUserData, message_id: int, **params):
        for_step: dict = params.pop('for_step', None)
        super().notify(user, message_id, **params)
        if for_step:
            self.bot.register_next_step_handler(**for_step)
