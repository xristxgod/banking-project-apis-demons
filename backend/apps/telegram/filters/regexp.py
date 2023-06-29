import re

from telebot import types
from telebot.custom_filters import AdvancedCustomFilter


class Filter(AdvancedCustomFilter):
    key = 'regexp'

    def check(self, message: types.Message, pattern: str):
        return re.match(pattern, message.text)
