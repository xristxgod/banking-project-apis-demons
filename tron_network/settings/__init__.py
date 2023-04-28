from __future__ import absolute_import

from ._load_settings import load_settings

from .common import *

try:
    from .dev import *
except ImportError:
    pass


env = load_settings.obj
