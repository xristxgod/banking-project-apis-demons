from telebot import types
from telebot.callback_data import CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter


class Filter(AdvancedCustomFilter):
    key = 'cq_filter'

    def check(self, call: types.CallbackQuery, cq_filter: CallbackDataFilter):
        return cq_filter.check(query=call)