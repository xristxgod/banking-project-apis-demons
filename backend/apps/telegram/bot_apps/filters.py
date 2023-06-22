from telebot import types
from telebot.callback_data import CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter


class ConfigFilter(AdvancedCustomFilter):
    key = 'config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)
