import copy

import pytest
from unittest.mock import Mock

from telebot import types

from apps.users.tests.factories import UserFactory

from telegram.middlewares.request import Request
from telegram.bot_apps.base.handlers import AbstractHandler


class ABCHandler(AbstractHandler):
    def attach(self): ...

    def call_without_auth(self, request) -> dict:
        return dict(typ='without_auth')

    def call(self, request) -> dict:
        return dict(typ='auth')


@pytest.mark.django_db
class TestAbstractHandler:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.bot = Mock()

        self.user = UserFactory()
        self.anonymous_user = types.User(id=666, is_bot=666, first_name='test')

        self.request = Request(
            user=self.user,
            call=Mock(), data='', text='', message_id=1, can_edit=True
        )
        self.anonymous_request = Request(
            user=self.anonymous_user,
            call=Mock(), data='', text='', message_id=1, can_edit=True
        )

    def test_auth(self):
        handlers = ABCHandler(self.bot)

        assert not handlers._is_anonymous(self.request)
        assert handlers._is_anonymous(self.anonymous_request)

        assert handlers._call_method(self.request) == {'typ': 'auth'}
        assert handlers._call_method(self.anonymous_request) == {'typ': 'without_auth'}

        handlers.use_auth = False

        assert handlers._call_method(self.request) == {'typ': 'auth'}
        assert handlers._call_method(self.anonymous_request) == {'typ': 'auth'}

    def test_is_step(self):
        handlers = ABCHandler(self.bot)

        handlers.storage[self.request.user.id] = {
                'step': {
                    'callback': None,
                    'set': True,
                },
                'data': {'test': 'test'},
            }

        request = copy.copy(self.request)

        assert handlers._is_step(request)

        assert request.can_edit
        assert request.message_id == 1

        handlers.post_notify(request)

        assert not request.can_edit
        assert request.message_id == 2

        handlers.storage.update(request.user.id, set_step=False)

        assert not handlers._is_step(request)
