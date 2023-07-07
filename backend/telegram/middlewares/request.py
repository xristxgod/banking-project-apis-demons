import re
from typing import Optional

from telebot import types

from telebot.handler_backends import BaseMiddleware

from telegram.middlewares.user import TelegramUser, AnonymousTelegramUser


class Request:
    def __init__(self, user: TelegramUser | AnonymousTelegramUser,
                 call: types.Message | types.CallbackQuery, **params):
        self.user = user
        self.call = call

        self.data: str = params['data']
        self.text: str = params['text']
        self.message_id: int = params['message_obj']

        self.can_edit: bool = params['can_edit']

        self.text_params = None
        if self.text.startswith('/') and len(self.text.split()) > 1:
            self.text_params = ' '.join(self.text.split()[1:])

    @property
    def has_text_params(self) -> bool:
        return self.text_params is not None


class Middleware(BaseMiddleware):
    @classmethod
    def _get_params(cls, call: types.Message | types.CallbackQuery) -> dict:
        if isinstance(call, types.Message):
            return dict(
                data=None,
                text=call.text,
                message_id=call.message_id,
                can_edit=False,
                message_obj=call,
            )
        else:
            return dict(
                data=call.data,
                text=call.message.text,
                message_id=call.message.message_id,
                can_edit=True,
                message_obj=call.message,
            )

    def __init__(self):
        super().__init__()
        self.update_types = ['message', 'callback_query']

    def pre_process(self, call: types.Message | types.CallbackQuery, data: dict):
        data['request'] = Request(
            user=data['user'],
            call=call,
            **self._get_params(call),
        )

    def post_process(self, message, data, exception):
        del data['request']
