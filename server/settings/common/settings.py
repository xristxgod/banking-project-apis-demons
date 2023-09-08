from __future__ import absolute_import

import os

NETWORK = os.getenv('NETWORK', 'COMMON')

DATABASE_URL = os.getenv('DATABASE_URL')
