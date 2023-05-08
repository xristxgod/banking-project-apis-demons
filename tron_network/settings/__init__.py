from __future__ import absolute_import

import os

from common import *

if os.getenv('NETWORK').upper() == 'DEV':
    from .dev import *
elif os.getenv('NETWORK').upper() == 'TEST':
    from .test import *
