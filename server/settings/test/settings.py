from __future__ import absolute_import

from settings.common import ASYNC_DATABASE_URL, DATABASE_URL

DATABASES = {
    # Async databases
    'default': ASYNC_DATABASE_URL + '/tests-merchant-db',
    'exchange-rate': ASYNC_DATABASE_URL + '/tests-exchange-rate-db',
    # Sync databases
    'sync:default': DATABASE_URL + '/tests-merchant-db',
    'sync:exchange-rate': DATABASE_URL + '/tests-exchange-rate-db',
}
