from __future__ import absolute_import

from .settings import *

try:
    from .local_settings import *
except ImportError:
    pass
