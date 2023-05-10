from __future__ import absolute_import

import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = ROOT_DIR / 'config'

NODE_URL = os.getenv('NODE_URL')

DEFAULT_FEE_LIMIT = 40_000_000

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
