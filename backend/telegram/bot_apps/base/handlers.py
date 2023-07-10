import abc

import telebot
from telebot import types

from telegram.middlewares.request import Request


class AbstractHandler(metaclass=abc.ABCMeta):
    use_auth = True

    parse_mode = 'Markdown'

    @classmethod
    def _is_anonymous(cls, request: Request):
        return isinstance(request.user, types.User)

    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot
        self.attach()

    def _call_method(self, request: Request) -> dict:
        if self.use_auth and self._is_anonymous(request):
            return self.call_without_auth(request)
        else:
            return self.call(request)

    def _handler(self, request: Request):
        return self.notify(
            request=request,
            params=self._call_method(request),
        )

    def __call__(self, _, data: dict):
        return self._handler(request=data['request'])

    def notify(self, request: Request, params: dict):
        if request.can_edit:
            self.bot.edit_message_text(
                chat_id=request.user.id,
                message_id=request.message_id,
                parse_mode=self.parse_mode,
                **params,
            )
        else:
            self.bot.send_message(
                chat_id=request.user.id,
                parse_mode=self.parse_mode,
                **params,
            )

    def post_notify(self, request: Request):
        pass

    @abc.abstractmethod
    def attach(self): ...

    @abc.abstractmethod
    def call_without_auth(self, request: Request) -> dict: ...

    @abc.abstractmethod
    def call(self, request: Request) -> dict: ...
