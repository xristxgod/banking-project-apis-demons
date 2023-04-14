from .common import *

from pydantic import BaseSettings

if os.getenv('TESTNET'):
    from .testnet import *

from ._manager import take_central_wallet_info


class Settings(BaseSettings):
    ROOT_DIR = ROOT_DIR
    CONFIG_DIR = CONFIG_DIR

    WALLET_INDEX_FILE = WALLET_INDEX_FILE

    NODE_URL: str = NODE_URL
    CENTRAL_WALLET: dict = take_central_wallet_info(CENTRAL_WALLET_CONFIG)

    @classmethod
    async def setup(cls):
        if not cls.CONFIG_DIR.is_dir():
            cls.CONFIG_DIR.mkdir()
        if not cls.WALLET_INDEX_FILE.is_file():
            open(cls.WALLET_INDEX_FILE, 'r').close()


settings = Settings()
