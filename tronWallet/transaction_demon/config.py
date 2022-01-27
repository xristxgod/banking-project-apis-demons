import os
from logging import getLogger
from decimal import Context

from dotenv import load_dotenv
from tronpy.providers import HTTPProvider

load_dotenv()

decimals = Context()
decimals.prec = 8

network = os.getenv("Network").lower()

DataBaseUrl = os.getenv("DataBaseURL")
Queue = os.getenv("Queue")
QueueBalancer = os.getenv("QueueBalancer")
RabbitMQURL = os.getenv("RabbitMQURL")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, "files")
if "files" not in os.listdir(ROOT_DIR):
    os.mkdir(BASE_DIR)

if network == "mainnet":
    __token = "tokens/tokensMainNet.json"
    USDT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    USDC = "TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8"
elif network == "shasta":
    __token = "tokens/tokensShastaNet.json"
    USDT = "TRvz1r3URQq5otL7ioTbxVUfim9RVSm1hA"
    USDC = "TK8fX7TpZqedXNYVn6RA24Xcxqox7hbn59"
else:
    __token = "tokens/tokensNileNet.json"
    USDT = "TF17BgPaZYbz8oxbjhriubPDsA7ArKoLX3"
    USDC = "TLBaRhANQoJFTqre9Nf1mjuwNWjCJeYqUL"
# File for TRC20 tokens
fileTokens = os.path.join(BASE_DIR, __token)

ERROR = os.path.join(BASE_DIR, "error.txt")
NOT_SEND = os.path.join(BASE_DIR, 'not_send')
NOT_SEND_TO_TRANSACTION = os.path.join(BASE_DIR, 'not_sent_to_transaction')
LAST_BLOCK = os.path.join(BASE_DIR, "last_block.txt")

if 'not_send' not in os.listdir(BASE_DIR):
    os.mkdir(NOT_SEND)
if 'not_sent_to_transaction' not in os.listdir(BASE_DIR):
    os.mkdir(NOT_SEND_TO_TRANSACTION)
node = os.getenv("NodeURL")
AdminAddress = os.getenv("ADMIN_WALLET")

logger = getLogger(__name__)
