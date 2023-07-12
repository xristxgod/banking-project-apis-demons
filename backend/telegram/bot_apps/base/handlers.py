import abc
from typing import Callable

import telebot
from telebot import types

from telegram.middlewares.request import Request
from telegram.bot_apps.base.storage import MemoryStorage


class AbstractHandler(metaclass=abc.ABCMeta):
    use_auth = True

    parse_mode = 'Markdown'
    cls_storage = MemoryStorage
    storage_key: str

    @classmethod
    def _is_anonymous(cls, request: Request):
        return isinstance(request.user, types.User)

    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot
        self.storage = self.cls_storage(self.storage_key or self)
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

    def _is_step(self, request: Request):
        return (
                self.storage.has(request.user.id) and
                self.storage[request.user.id]['step']['set']
        )

    def __call__(self, _, data: dict):
        request = data['request']
        if self._is_step(request):
            request.text = _.text
            request.call = _
        return self._handler(request=request)

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
        self.post_notify(request)

    def post_notify(self, request: Request):
        if self.storage.get(request.user.id) and self.storage[request.user.id]['step']['set']:
            request.can_edit = False
            request.message_id += 1
            self.bot.register_next_step_handler_by_chat_id(
                chat_id=request.user.id,
                callback=self.storage[request.user.id]['step']['callback'] or self,
                data={
                    'request': request,
                }
            )

    @abc.abstractmethod
    def attach(self): ...

    @abc.abstractmethod
    def call_without_auth(self, request: Request) -> dict: ...

    @abc.abstractmethod
    def call(self, request: Request) -> dict: ...
