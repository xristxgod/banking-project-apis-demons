from typing import Optional

from telebot import types
from telebot.handler_backends import BaseMiddleware

from apps.telegram.models import User


# TODO add cache func
def cached_user(user_id: int) -> Optional[User]:
    user = User.objects.filter(pk=user_id)
    if user.exists():
        return user
    return None


class UserMiddleware(BaseMiddleware):
    def pre_process(self, message, data: dict):
        # TODO не трогать калбеки
        data['user'] = cached_user(message.from_user.id)

    def post_process(self, message, data: dict, exception: Exception):
        del data['user']
