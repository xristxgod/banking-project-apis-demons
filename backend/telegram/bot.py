import logging

import telebot

from django.conf import settings


class BaseBot:

    @classmethod
    def get_logger(cls):
        logger = telebot.logger
        logger.setLevel(logging.INFO)
        logger.setLevel(logging.ERROR)
        return logger

    def __init__(self, token: str, use_logger: bool = True):
        self.bot = telebot.TeleBot(token=token, use_class_middlewares=True)
        if use_logger:
            setattr(self, 'logger', self.get_logger())

        self.setup()

    def setup(self):
        self.setup_middleware()
        self.setup_custom_filter()
        self.setup_handlers()
        self.setup_step_controller()

    def setup_step_controller(self):
        self.bot.enable_save_next_step_handlers(delay=2)
        self.bot.load_next_step_handlers()

    def setup_middleware(self): ...

    def setup_custom_filter(self): ...

    def setup_handlers(self): ...


class MainBot(BaseBot):
    def setup_middleware(self):
        from telegram import middlewares
        self.bot.setup_middleware(middlewares.UserMiddleware())
        self.bot.setup_middleware(middlewares.RequestMiddleware())

    def setup_custom_filter(self):
        from telegram import filters
        self.bot.add_custom_filter(filters.CallbackQueryFilter())
        self.bot.add_custom_filter(filters.RegexpFilter())

    def setup_handlers(self):
        from telegram.bot_apps import ALL_HANDLERS
        for handler in ALL_HANDLERS:
            handler(self.bot)


main_bot = MainBot(settings.MAIN_TELEGRAM_BOT_TOKEN)
