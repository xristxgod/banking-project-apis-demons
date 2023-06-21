from __future__ import absolute_import

from .common import *

if os.getenv('NETWORK', 'DEV') == 'DEV':
    from .dev import *