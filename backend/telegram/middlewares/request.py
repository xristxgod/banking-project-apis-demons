import re
from typing import Optional

from telebot import types

from telebot.handler_backends import BaseMiddleware

from telegram.middlewares.user import TelegramUser, AnonymousTelegramUser


class TelegramRequest:
    def __init__(self, user: TelegramUser | AnonymousTelegramUser, **params):
        self.user = user
        self.data: str = params['data']
        self.text: str = params['text']
        self.message_id: int = params['message_id']
        self._can_edit: bool = params['can_edit']
        self.message_obj = params['message_obj']

        self.trigger_step = False

    @property
    def text_params(self) -> Optional[str]:
        if len(self.text.split()) > 1:
            return ' '.join(self.text.split()[1:])

    @property
    def can_edit(self) -> bool:
        return self._can_edit

    @can_edit.setter
    def can_edit(self, value: bool):
        self._can_edit = value

    def valid_text_params(self, pattern: str) -> bool:
        return re.match(pattern, self.text_params) is not None


class Middleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.update_types = ['message', 'callback_query']

    def pre_process(self, call: types.Message | types.CallbackQuery, data: dict):
        if isinstance(call, types.Message):
            params = dict(
                data=None,
                text=call.text,
                message_id=call.message_id,
                can_edit=False,
                message_obj=call,
            )
        else:
            params = dict(
                data=call.data,
                text=call.message.text,
                message_id=call.message.message_id,
                can_edit=True,
                message_obj=call.message,
            )

        data['request'] = TelegramRequest(
            user=data['user'],
            **params,
        )

    def post_process(self, message, data, exception):
        del data['request']
