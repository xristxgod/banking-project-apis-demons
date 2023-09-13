from __future__ import absolute_import

import os

NETWORK = os.getenv('NETWORK', 'COMMON')

DATABASE_URL = os.getenv('DATABASE_URL', '').replace('postgresql', 'postgresql+asyncpg')

DATABASES = {
    'default': DATABASE_URL + '/merchant-db',
    'exchange-rate': DATABASE_URL + '/exchange-rate-db',
}
