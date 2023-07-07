from telebot import types
from telebot.handler_backends import BaseMiddleware

from apps.users import models


class Middleware(BaseMiddleware):
    @classmethod
    def get_user(cls, from_user: types.User) -> types.User | models.User:
        user = from_user.id
        if obj := models.User.objects.filter(id=from_user.id).first():
            user = obj
        setattr(user, 'is_anonymous', isinstance(obj, models.User))
        return user

    def __init__(self):
        super().__init__()
        self.update_types = ['message', 'callback_query']

    def pre_process(self, call, data):
        data['user'] = self.get_user(call.from_user)

    def post_process(self, call, data, exception):
        del data['user']
