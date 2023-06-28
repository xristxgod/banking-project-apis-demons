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


class Middleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ['message', 'callback_query']

    @classmethod
    def _get_user(cls, from_user: types.User) -> BaseUserData:
        qs = models.User.objects.filter(id=from_user.id)

        if qs.exists():
            return UserData(obj=qs.first())

        return AnonymousUserData(obj= from_user)

    def pre_process(self, call: types.Message | types.CallbackQuery, data: dict):
        data['user'] = self._get_user(call.from_user)

    def post_process(self, call: types.Message, data: dict, exception=None):
        del data['user']
