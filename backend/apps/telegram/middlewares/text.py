from telebot import types
from telebot.handler_backends import BaseMiddleware


class Middleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ['message']

    def pre_process(self, message: types.Message, data: dict):
        text_params = None
        if len(message.text.split()) > 1:
            text_params = ' '.join(message.text.split()[1:])

        data['text_params'] = text_params

    def post_process(self, call: types.Message, data: dict, exception=None):
        del data['text_params']
