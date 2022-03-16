import os
from logging import getLogger
from decimal import Context

from dotenv import load_dotenv

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
    __token, USDT, USDC = (
        "tokens/tokensMainNet.json", "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t", "TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8"
    )
elif network == "shasta":
    __token, USDT, USDC = (
        "tokens/tokensShastaNet.json", "TRvz1r3URQq5otL7ioTbxVUfim9RVSm1hA", "TK8fX7TpZqedXNYVn6RA24Xcxqox7hbn59"
    )
else:
    __token, USDT, USDC = (
        "tokens/tokensNileNet.json", "TF17BgPaZYbz8oxbjhriubPDsA7ArKoLX3", "TLBaRhANQoJFTqre9Nf1mjuwNWjCJeYqUL"
    )

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
AdminAddress = os.getenv("AdminWallet")
ReportingAddress = os.getenv("ReportingAddress")

ElasticLogServer = os.getenv("ELASTIC_LOG_SERVER")
ElasticLogin = os.getenv("ELASTIC_LOGIN")
ElasticPassword = os.getenv("ELASTIC_PASSWORD")
ElasticLogIndex = os.getenv('ELASTIC_LOG_INDEX')
ElasticLogIndexEx = f"{os.getenv('ELASTIC_LOG_INDEX_EX')}-demon"

logger = getLogger(__name__)