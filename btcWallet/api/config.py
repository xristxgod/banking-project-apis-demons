from decimal import Context, Decimal
from logging import getLogger
import os
from dotenv import load_dotenv

load_dotenv()

logger = getLogger(__name__)

decimal = Context()
decimal.prec = 8

ADMIN_ADDRESS = os.getenv('ADMIN_WALLET', '188c31hPxLcZekAG9JXZX97mDtshaqYC3z')
ADMIN_FEE = decimal.create_decimal(os.getenv('ADMIN_FEE', '0.00005'))

DUST_MULTIPLICATOR = int(os.getenv('DUST_MULTIPLICATOR', 2))

DB_URL = os.getenv("DataBaseURL")

BIP32_ROOT_KEY = os.getenv(
    'BIP32_ROOT_KEY',
    'xprv'
)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, 'files')

if 'files' not in os.listdir(ROOT_DIR):
    os.mkdir(BASE_DIR)

SUB_WALLET_INDEX_FILE = os.path.join(BASE_DIR, 'walletIndex.txt')

if 'walletIndex.txt' not in os.listdir(BASE_DIR):
    with open(SUB_WALLET_INDEX_FILE, 'w') as file:
        file.write('1')
