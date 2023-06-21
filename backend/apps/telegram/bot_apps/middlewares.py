from telebot import types
from telebot.handler_backends import BaseMiddleware

from apps.users.models import User

__all__ = (
    'UserMiddleware',
)


class UserMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ['message', 'callback_query']

    def pre_process(self, message: types.Message, data):
        data['user'] = User

    def post_process(self, message: types.Message, data, exception):
        del data['user']
