from __future__ import absolute_import

import os

NETWORK = os.getenv('NETWORK', 'COMMON')

BACKEND_SECRET_KEY = os.getenv('BACKEND_SECRET_KEY')

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

RABBITMQ_URL = os.getenv('RABBITMQ_URL', '')
REDIS_URL = os.getenv('REDIS_URL', '')

CACHED_BACKEND_URL = REDIS_URL + '/1'
DAEMON_STORAGE_BACKEND_URL = REDIS_URL + '/2'
ADMIN_CACHED_BACKEND_URL = REDIS_URL + '/3'

CELERY_BROKER_URL = RABBITMQ_URL
CELERY_RESULT_BACKEND = REDIS_URL + '/4'
CELERY_TASK_DEFAULT_QUEUE = 'celery'
CELERY_BATCHES_QUEUE = 'sl_salary_batches'
CELERY_BROKER_TRANSPORT_OPTIONS = {'confirm_publish': True}
CELERY_ACCEPT_CONTENT = {'json', 'application/json'}
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

EXCHANGERATE_API_KEY = os.getenv('EXCHANGERATE_API_KEY')

BLOCKCHAIN_CENTRAL_WALLETS = {
    'eth': {
        'address': os.getenv('BLOCKCHAIN_CENTRAL_WALLET_ADDRESS_ETH'),
        'private_key': os.getenv('BLOCKCHAIN_CENTRAL_WALLET_PRIVATE_KEY_ETH'),
        'mnemonic': os.getenv('BLOCKCHAIN_CENTRAL_WALLET_MNEMONIC_ETH'),
    },
    'bsc': {
        'address': os.getenv('BLOCKCHAIN_CENTRAL_WALLET_ADDRESS_BSC'),
        'private_key': os.getenv('BLOCKCHAIN_CENTRAL_WALLET_PRIVATE_KEY_BSC'),
        'mnemonic': os.getenv('BLOCKCHAIN_CENTRAL_WALLET_MNEMONIC_BSC'),
    },
    'tron': {
        'address': os.getenv('BLOCKCHAIN_CENTRAL_WALLET_ADDRESS_TRON'),
        'private_key': os.getenv('BLOCKCHAIN_CENTRAL_WALLET_PRIVATE_KEY_TRON'),
        'mnemonic': os.getenv('BLOCKCHAIN_CENTRAL_WALLET_MNEMONIC_TRON'),
    },
}

ADMIN_CREDENTIALS = {
    'username': os.getenv('ADMIN_USERNAME'),
    'password': os.getenv('ADMIN_PASSWORD'),
}

USE_AUTHORISATIONS = {
    'swagger': True,
    'admin': True,
    'admin-exchange-rate': True,
}
