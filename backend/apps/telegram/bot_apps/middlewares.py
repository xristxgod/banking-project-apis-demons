import decimal

from telebot import types
from telebot.handler_backends import BaseMiddleware

from apps.users import models


class BaseUserData:
    def __init__(self, obj: types.User | models.User):
        self.obj = obj

    @property
    def is_anonymous(self) -> bool:
        raise NotImplementedError()

    @property
    def chat_id(self) -> int:
        return self.obj.id

    id = chat_id

    @property
    def username(self) -> str:
        return self.obj.username


class AnonymousUserData(BaseUserData):
    @property
    def is_anonymous(self) -> bool:
        return True


class UserData(AnonymousUserData):
    @property
    def is_anonymous(self) -> bool:
        return False

    @property
    def balance(self) -> decimal.Decimal:
        # TODO: add short cache func
        from apps.users.services import get_balance
        return get_balance(self.obj)


class UserMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ['message', 'callback_query']

    def pre_process(self, call: types.Message | types.CallbackQuery, data: dict):
        qs = models.User.objects.filter(id=call.from_user.id)

        if qs.exists():
            user = UserData(obj=qs.first())
        else:
            user = AnonymousUserData(call.from_user)

        data['user'] = user

    def post_process(self, call: types.Message, data: dict, exception=None):
        del data['user']


class TextParamsMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ['message']

    def pre_process(self, message: types.Message, data: dict):
        text_params = None
        if len(message.text.split()) > 1:
            text_params = message.text.split()[1:]

        data['text_params'] = text_params

    def post_process(self, call: types.Message, data: dict, exception=None):
        del data['text_params']
