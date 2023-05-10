from __future__ import absolute_import

from settings.common import CONFIG_DIR, APPS_MODELS

DATABASE_PATH = CONFIG_DIR / 'test.db'

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
