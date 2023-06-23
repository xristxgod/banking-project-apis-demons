import decimal

from telebot import types
from telebot.handler_backends import BaseMiddleware

from apps.users.models import User

__all__ = (
    'UserMiddleware',
)


class UserData:
    def __init__(self, obj: User):
        self.obj = obj

    @property
    def chat_id(self) -> int:
        return self.obj.chat_id

    @property
    def username(self) -> str:
        return self.obj.username

    @property
    def balance(self) -> decimal.Decimal:
        from apps.users.services import get_balance
        return get_balance(self.obj)


class UserMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ['message', 'callback_query']

    def pre_process(self, msg_or_cq: types.Message | types.CallbackQuery, data: dict):
        qs = User.objects.filter(chat_id=msg_or_cq.from_user.id)

        user = None
        if qs.exists():
            user = UserData(
                obj=qs.first()
            )

        data['user'] = user

    def post_process(self, msg_or_cq: types.Message, data: dict, exception=None):
        del data['user']
