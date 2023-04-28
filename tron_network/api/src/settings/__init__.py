from .common import *

from pydantic import BaseSettings

if os.getenv('TESTNET'):
    from .testnet import *

from . import _manager


class Settings(BaseSettings):
    ROOT_DIR = ROOT_DIR
    CONFIG_DIR = CONFIG_DIR

    WALLET_INDEX_FILE = WALLET_INDEX_FILE

    NODE_URL: str = NODE_URL
    CENTRAL_WALLET: dict = _manager.take_central_wallet_info(CENTRAL_WALLET_CONFIG)
    GLOBAL_FEE_LIMIT = GLOBAL_FEE_LIMIT
    ENCODE_SECRET_KEY = _manager.take_encode_secret_key(ENCODE_SECRET_KEY_CONFIG, IS_ENCODE)

    async def setup(self):
        if not self.CONFIG_DIR.is_dir():
            self.CONFIG_DIR.mkdir()
        if not self.WALLET_INDEX_FILE.is_file():
            open(self.WALLET_INDEX_FILE, 'w').close()


settings = Settings()
