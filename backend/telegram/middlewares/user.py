from telebot import types
from telebot.handler_backends import BaseMiddleware

from apps.users import models
from apps.users.services import get_balance


class AnonymousTelegramUser:
    def __init__(self, obj):
        self.obj = obj

    @property
    def is_anonymous(self):
        return True

    @property
    def chat_id(self) -> int:
        return self.obj.id

    @property
    def username(self) -> str:
        return self.obj.username


class TelegramUser(AnonymousTelegramUser):
    def __init__(self, obj: models.User):
        from apps.orders.models import OrderStatus, Deposit
        super().__init__(obj)
        self.deposit = Deposit.objects.filter(
            order__user=self.obj,
            order__status=OrderStatus.CREATED,
        ).first()

    @property
    def is_anonymous(self):
        return False

    @property
    def balance(self):
        return get_balance(self.obj)

    @property
    def has_active_deposit(self) -> bool:
        return self.deposit is not None


class Middleware(BaseMiddleware):
    @classmethod
    def get_user(cls, from_user: types.User) -> AnonymousTelegramUser | TelegramUser:
        if obj := models.User.objects.filter(id=from_user.id).first():
            return TelegramUser(obj)
        return AnonymousTelegramUser(from_user)

    def __init__(self):
        super().__init__()
        self.update_types = ['message', 'callback_query']

    def pre_process(self, call, data):
        data['user'] = self.get_user(call.from_user)

    def post_process(self, message, data, exception):
        del data['user']
