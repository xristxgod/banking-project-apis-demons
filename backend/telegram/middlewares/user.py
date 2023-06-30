from telebot import types
from telebot.handler_backends import BaseMiddleware

from apps.users import models


class AnonymousTelegramUser:
    def __init__(self, obj):
        self.obj = obj

    @property
    def is_anonymous(self):
        return True

    @property
    def chat_id(self) -> int:
        return self.obj.id


class TelegramUser(AnonymousTelegramUser):
    @property
    def is_anonymous(self):
        return False


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
