import os
import logging
import decimal


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


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

    ADMIN_WALLET_ADDRESS = os.getenv("ADMIN_WALLET_ADDRESS")
    ADMIN_WALLET_PRIVATE_KEY = os.getenv("ADMIN_WALLET_PRIVATE_KEY")
    ADMIN_FEE = os.getenv("ADMIN_FEE")
    ADMIN_FEE_TOKEN = os.getenv("ADMIN_FEE_TOKEN")

    REPORTING_ADDRESS = os.getenv("REPORTING_ADDRESS")
