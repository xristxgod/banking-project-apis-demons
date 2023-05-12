from __future__ import absolute_import

from .common import *

NETWORK = os.getenv('NETWORK', '').upper()

if NETWORK == 'DEV':
    from .dev import *
elif NETWORK == 'TEST':
    from .test import *
