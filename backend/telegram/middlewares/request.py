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
        self.cen_edit: bool = params['can_edit']

    @property
    def text_params(self) -> Optional[str]:
        if len(self.text.split()) > 1:
            return ' '.join(self.text.split()[1:])


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
                cen_edit=False,
            )
        else:
            params = dict(
                data=call.data,
                text=call.message.text,
                message_id=call.message.message_id,
                cen_edit=True,
            )

        data['request'] = TelegramRequest(
            user=data['user'],
            **params,
        )

    def post_process(self, message, data, exception):
        del data['request']
