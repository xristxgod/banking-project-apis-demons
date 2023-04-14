import os
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent.parent
CONFIG_DIR = ROOT_DIR / 'config'

WALLET_INDEX_FILE = CONFIG_DIR / 'index.txt'

NODE_URL = os.getenv('NODE_URL')
GLOBAL_FEE_LIMIT = 40_000_000

CENTRAL_WALLET_CONFIG = {
    'manager': 'SecretStorage',
    'wallet': {
        'address': os.getenv('CENTRAL_WALLET_ADDRESS_LABEL'),
        'private_key': os.getenv('CENTRAL_WALLET_PRIVATE_KEY_LABEL'),
        'mnemonic': os.getenv('CENTRAL_WALLET_MNEMONIC_LABEL'),
    }
}