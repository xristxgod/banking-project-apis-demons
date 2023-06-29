import decimal
from typing import Optional

from telebot import types
from telebot.handler_backends import BaseMiddleware

from apps.users import models
from apps.orders.models import OrderStatus, Deposit


class BaseUserData:
    def __init__(self, obj: types.User | models.User):
        self.obj = obj
        self.deposit = self._take_active_deposit()

    def _take_active_deposit(self) -> Deposit:
        qs = Deposit.objects.filter(
            order__user=self.obj,
            order__status=OrderStatus.CREATED,
        )
        if qs.exists():
            return qs.first()

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

    @property
    def active_deposit(self) -> Optional[Deposit]:
        return self.deposit


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
