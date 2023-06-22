from telebot import types
from telebot.handler_backends import BaseMiddleware

from apps.users.models import User

__all__ = (
    'UserMiddleware',
)


class UserMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ['message', 'callback_query']

    def pre_process(self, msg_or_cq: types.Message | types.CallbackQuery, data: dict):
        qs = User.objects.filter(chat_id=msg_or_cq.from_user.id)

        user = None
        if qs.exists():
            user = qs.first()

        data['user'] = user

    def post_process(self, msg_or_cq: types.Message, data: dict, exception=None):
        del data['user']
