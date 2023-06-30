import abc

import telebot

from telegram.middlewares.request import TelegramRequest

__all__ = (
    'AbstractHandler',
)


class AbstractHandler(metaclass=abc.ABCMeta):
    use_auth = True

    parse_mode = 'Markdown'

    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot
        self.attach()

    def _get_params(self, request: TelegramRequest):
        if self.use_auth and request.user.is_anonymous:
            return self.call_without_auth(request)
        else:
            return self.call(request)

    def _handler(self, request: TelegramRequest):
        params = self._get_params(request)
        return self.notify(
            request=request,
            **params,
        )

    def __call__(self, _, data: dict):
        return self._handler(request=data['request'])

    def notify(self, request: TelegramRequest, **params):
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
    def call_without_auth(self, request: TelegramRequest) -> dict: ...

    @abc.abstractmethod
    def call(self, request: TelegramRequest) -> dict: ...
