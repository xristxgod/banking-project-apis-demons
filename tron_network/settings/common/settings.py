from __future__ import absolute_import

import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = ROOT_DIR / 'config'

NODE_URL = os.getenv('NODE_URL')

DEFAULT_FEE_LIMIT = 40_000_000
# With what frequency the buffer will be cleared. In minutes.
TRANSACTION_BUFFER_CLEAR_TIME = 20

APPS_MODELS = (
    'core.crypto.models',
)

DATABASE_PATH = CONFIG_DIR / 'db.db'

DATABASE_CONFIG = {
    'connections': {
        'master': f'sqlite:///{DATABASE_PATH}',
    },
    'apps': {
        'models': {
            'models': APPS_MODELS,
            'default_connection': "master",
        }
    },
    'timezone': 'UTC',
}

CENTRAL_WALLET_CONFIG = {
    'address': os.getenv('CENTRAL_WALLET_ADDRESS'),
    'private_key': os.getenv('CENTRAL_WALLET_PRIVATE_KEY')
}

REDIS_URL = os.getenv('INTERNAL_REDIS_URL')
RABBITMQ_URL = os.getenv('INTERNAL_RABBITMQ_URL')


BALANCER_CONFIG = {}
DAEMON_CONFIG = {}