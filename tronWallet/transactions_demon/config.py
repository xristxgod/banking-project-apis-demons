import os
from dotenv import load_dotenv
from logging import getLogger
from tronpy.providers import HTTPProvider, AsyncHTTPProvider

load_dotenv()
# The path to the database
DataBaseUrl = os.getenv("DataBaseURL")
# Queue name for RabbitMQ
Queue = os.getenv("Queue")

if os.getenv("isRabbitLocal").title() == "True":
    RabbitMQURL = "localhost"
else:
    RabbitMQURL = os.getenv("RabbitMQURL")

network = os.getenv("NETWORK")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, "files")

if "files" not in os.listdir(ROOT_DIR):
    os.mkdir(BASE_DIR)

ERROR = os.path.join(BASE_DIR, "error.txt")
NOT_SEND = os.path.join(BASE_DIR, 'not_send')
LAST_BLOCK = os.path.join(BASE_DIR, "last_block.txt")

if 'not_send' not in os.listdir(BASE_DIR):
    os.mkdir(NOT_SEND)

if network.title() in ["Shasta", "Nile"]:
    TronGridApiKey = None
    asyncTronGridApiKey = None
else:
    if str(os.getenv("MultiKeys")).title() == "True":
        TronGridApiKey = HTTPProvider(api_key=os.getenv("listTronGridAPIKEY").split())
        asyncTronGridApiKey = AsyncHTTPProvider(api_key=os.getenv("TronGridAPIKEY"))
    else:
        TronGridApiKey = HTTPProvider(api_key=os.getenv("TronGridAPIKEY"))
        asyncTronGridApiKey = AsyncHTTPProvider(api_key=os.getenv("TronGridAPIKEY"))

if network.title() == "Mainnet":
    full_node, solidity_node, event_server = (HTTPProvider("https://api.trongrid.io"), )*3
    # Async providers
    async_full_node, async_solidity_node, async_event_server = (AsyncHTTPProvider("https://api.trongrid.io"), )*3
elif network.title() == "Shasta":
    full_node, solidity_node, event_server = (HTTPProvider("https://api.shasta.trongrid.io"), )*3
    # Async providers
    async_full_node, async_solidity_node, async_event_server = (AsyncHTTPProvider("https://api.shasta.trongrid.io"), )*3
elif network.title() == "Nile":
    full_node, solidity_node, event_server = (HTTPProvider("https://nile.trongrid.io"), )*3
    # Async providers
    async_full_node, async_solidity_node, async_event_server = (AsyncHTTPProvider("https://nile.trongrid.io"), )*3
else:
    raise Exception("Specify the correct network")

provider = dict(full_node=full_node, solidity_node=solidity_node, event_server=event_server)
async_provider = dict(full_node=async_full_node, solidity_node=async_solidity_node, event_server=async_event_server)

logger = getLogger(__name__)