from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

from apps.telegram.models import User


class UserDatabaseMiddleware(LifetimeControllerMiddleware):
    def __init__(self):
        super().__init__()

    async def pre_process(self, obj, data, *args):
        data['user'] = None

        if not hasattr(obj, "update_id"):
            data['user'] = User.get_or_none(pk=obj['from']['id'])

    async def post_process(self, obj, data, *args):
        if 'user' in data.keys():
            del data['user']
