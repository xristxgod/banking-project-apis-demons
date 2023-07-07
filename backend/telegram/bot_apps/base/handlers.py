import abc

import telebot
from telebot import types

from telegram.middlewares.request import Request


class AbstractHandler(metaclass=abc.ABCMeta):
    use_auth = True

    parse_mode = 'Markdown'

    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot
        self.attach()

    def _get_params(self, request: Request):
        if self.use_auth and request.user.is_anonymous:
            return self.call_without_auth(request)
        else:
            return self.call(request)

    def _handler(self, request: Request):
        params = self._get_params(request)
        return self.notify(
            request=request,
            **params,
        )

    def __call__(self, _, data: dict):
        return self._handler(request=data['request'])

    def notify(self, request: Request, **params):
        if request.can_edit:
            self.bot.edit_message_text(
                chat_id=request.user.chat_id,
                message_id=request.message_id,
                parse_mode=self.parse_mode,
                **params,
            )
        else:
            self.bot.send_message(
                chat_id=request.user.chat_id,
                parse_mode=self.parse_mode,
                **params,
            )

    @abc.abstractmethod
    def attach(self): ...

    @abc.abstractmethod
    def call_without_auth(self, request: Request) -> dict: ...

    @abc.abstractmethod
    def call(self, request: Request) -> dict: ...


class StepMixin:

    def _step_call(self, message: types.Message, data: dict):
        old_request: Request = data['request']
        data['request'] = Request(
            user=old_request.user,
            data=data.get('data') or old_request.data,
            text=message.text,
            message_id=message.message_id,
            can_edit=False,
            message_obj=message,
        )
        return self.__call__(message, data)

    @abc.abstractmethod
    def by_step(self, request: Request): ...

    def notify(self, request: Request, **params):
        super().notify(request, **params)
        if request.trigger_step:
            self.bot.register_next_step_handler(
                callback=self._step_call,
                message=request.message_obj,
                data=dict(
                    request=request,
                )
            )
        else:
            self.bot.clear_step_handler_by_chat_id(request.user.chat_id)
