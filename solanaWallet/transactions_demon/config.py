import os
from datetime import datetime
from dotenv import load_dotenv
from logging import getLogger


logger = getLogger(__name__)


load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Errors Recording
ERROR = os.path.join(BASE_DIR, 'error.txt')
# Errors Recording
LAST_BLOCK_LOG = os.path.join(BASE_DIR, 'LAST_BLOCK.txt')

SOLANA_URL = os.getenv('SOLANA_URL', 'api.devnet.solana.com')


async def time_str_from_timestamp(t: int) -> str:
    return datetime.fromtimestamp(int(t)).strftime('%d-%m-%Y %H:%M:%S')
