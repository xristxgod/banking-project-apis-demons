from __future__ import absolute_import

import os

from .common import *


if os.environ.get('NETWORK') == 'DEV':
    from .dev import *
