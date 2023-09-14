from __future__ import absolute_import

import os

NETWORK = os.getenv('NETWORK', 'COMMON')

DATABASE_URL = os.getenv('DATABASE_URL', '')
ASYNC_DATABASE_URL = DATABASE_URL.replace('postgresql', 'postgresql+asyncpg')

DATABASES = {
    # Async databases
    'default': ASYNC_DATABASE_URL + '/merchant-db',
    'exchange-rate': ASYNC_DATABASE_URL + '/exchange-rate-db',
    # Sync databases
    'sync:default': DATABASE_URL + '/merchant-db',
    'sync:exchange-rate': DATABASE_URL + '/exchange-rate-db',
}
