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

RABBITMQ_URL = os.getenv('RABBITMQ_URL', '')
REDIS_URL = os.getenv('REDIS_URL', '')

CACHED_BACKEND_URL = REDIS_URL + '/1'
ADMIN_CACHED_BACKEND_URL = REDIS_URL + '/2'

CELERY_BROKER_URL = RABBITMQ_URL
CELERY_RESULT_BACKEND = REDIS_URL + '/3'
CELERY_TASK_DEFAULT_QUEUE = 'celery'
CELERY_BATCHES_QUEUE = 'sl_salary_batches'
CELERY_BROKER_TRANSPORT_OPTIONS = {'confirm_publish': True}
CELERY_ACCEPT_CONTENT = {'json', 'application/json'}
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

EXCHANGERATE_API_KEY = os.getenv('EXCHANGERATE_API_KEY')
