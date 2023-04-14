import os

from .common import *

from pydantic import BaseSettings

if os.getenv('TESTNET'):
    from .testnet import *


class Settings(BaseSettings):
    NODE_URL = NODE_URL


settings = Settings()
