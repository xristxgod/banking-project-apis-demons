import os
import logging
import decimal


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_DIR = os.path.join(ROOT_DIR, "file")

ERROR = os.path.join(FILE_DIR, "error.txt")
NOT_SEND = os.path.join(FILE_DIR, 'not_send')
LAST_BLOCK = os.path.join(FILE_DIR, "last_block.txt")

if "file" not in os.listdir(ROOT_DIR): os.mkdir(FILE_DIR)
if "not_send" not in os.listdir(FILE_DIR): os.mkdir(NOT_SEND)

decimals = decimal.Context()
decimals.prec = 8


logger = logging.getLogger(__name__)
logging.basicConfig(
    format=u"%(levelname)s:     %(filename)s line:%(lineno)d  %(message)s",
    level=logging.INFO
)


class Config:
    API_URL = os.getenv("API_URL")

    DATABASE_URL = os.getenv("DATABASE_URL")

    ELASTIC_LOG_SERVER = os.getenv("ELASTIC_LOG_SERVER")
    ELASTIC_LOG_INDEX_EX = f"{os.getenv('ELASTIC_LOG_INDEX_EX')}-api"
    ELASTIC_LOGIN = os.getenv("ELASTIC_LOGIN", "1241244")
    ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", "1241244")
    ELASTIC_LOG_INDEX = os.getenv("ELASTIC_LOG_INDEX")

    NGINX_DOMAIN = os.getenv("NGINX_DOMAIN")

    RABBITMQ_URL = os.getenv("RABBITMQ_URL")
    BALANCER_QUEUE = os.getenv("BALANCER_QUEUE")
    MAX_BALANCER_MESSAGE = int(os.getenv("MAX_BALANCER_MESSAGE", 1))

    NETWORK = os.getenv("NETWORK", "TESTNET")
    NODE_URL = os.getenv("NODE_URL", "http://tron-mainnet.mangobank.elcorp.io:8090")
    MIN_BALANCE = decimals.create_decimal(os.getenv("MIN_BALANCE_NATIVE", 10))

    ADMIN_WALLET_ADDRESS = os.getenv("ADMIN_WALLET_ADDRESS", "TWCQvcJ2JkWamoXWs7rAf7PiWTYaiB8WHx")
    ADMIN_WALLET_PRIVATE_KEY = os.getenv("ADMIN_WALLET_PRIVATE_KEY", "53054a7ebbda440df4f15b225def00dc8abc62a4a5a269a7c6023223a31d7032")
    ADMIN_FEE = os.getenv("ADMIN_FEE", 5.3)
    ADMIN_FEE_TOKEN = os.getenv("ADMIN_FEE_TOKEN", 18.4)

    REPORTING_ADDRESS = os.getenv("REPORTING_ADDRESS", "TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb")
