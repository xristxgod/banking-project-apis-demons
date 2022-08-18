import pika
import time
from tronpy.tron import Tron, HTTPProvider

from src_v1.utils.utils import is_block_ex, get_public_node, get_last_block
from src_v1.v1.wallet import wallet
from config import AdminWallet, min_balance, MAX_BALANCER_MESSAGE, BALANCER_QUEUE, RABBITMQ_URL, node, network


__node = Tron(provider=HTTPProvider(node) if network == "mainnet" else None, network=network)


# <<<------------------------------------>>> Node Status <<<--------------------------------------------------------->>>


def __get_node_info(our_node):
    if int(our_node.get_node_info()["activeConnectCount"]) == 0:
        # If there are no active connections to the node, then the node is dead!
        raise Exception("Problems with the node. There are no active connections")


def __get_is_block_ex(our_node, public_node):
    our_block = our_node.get_latest_block_number()
    public_block = public_node.get_latest_block_number()
    if not is_block_ex(
            our_block=our_block,
            public_block=public_block
    ):
        # If the blocks are moving with a large gap, then something is wrong with the node
        raise Exception("The blocks in the node are moving too slowly")


def __get_is_acc_admin(our_node):
    if not our_node.get_account(AdminWallet):
        # If you call out the method through the node, then something is also wrong
        raise Exception("The node is not working correctly")


def node_status() -> bool:
    """They will check whether the node is working or not. Lagging behind or not."""
    # Project (private) node
    our_node = __node
    # Public node
    public_node = get_public_node()
    try:
        __get_node_info(our_node=our_node)
    except Exception as error:
        time.sleep(2)
        __get_node_info(our_node=our_node)
    try:
        __get_is_block_ex(our_node=our_node, public_node=public_node)
    except Exception as error:
        time.sleep(2)
        __get_is_block_ex(our_node=our_node, public_node=public_node)

    try:
        __get_is_acc_admin(our_node=our_node)
    except Exception as error:
        time.sleep(2)
        __get_is_acc_admin(our_node=our_node)
    # Otherwise, everything is OK!
    return True


# <<<------------------------------------>>> Admin Balance Status <<<------------------------------------------------>>>


async def native_balance_status() -> bool:
    """Checks if there is a balance on the central wallet"""
    balance = (await wallet.get_balance(address=AdminWallet)).balance
    if balance == 0 and balance < min_balance:
        return False
    return True


# <<<------------------------------------>>> Demon Status <<<------------------------------------------------------->>>


def demon_status() -> bool:
    """Check the status of the daemon"""
    # Get the last block from the file last_block.txt
    demon_block: int = get_last_block()
    # Get the last block from the node
    our_block: int = __node.get_latest_block_number()
    # If the blocks are equal, or the gap is not critical, then everything is OK.
    if (our_block == demon_block) or (our_block - demon_block <= 25):
        return True
    # Otherwise, something is wrong.
    return False


# <<<------------------------------------>>> Balancer Status <<<----------------------------------------------------->>>


def balancer_status() -> bool:
    try:
        pika_conn_params = pika.URLParameters(url=RABBITMQ_URL)
        connection = pika.BlockingConnection(pika_conn_params)
        channel = connection.channel()
        queue_1 = channel.queue_declare(
            queue=BALANCER_QUEUE, durable=True,
            exclusive=False, auto_delete=False
        )
        q_1 = queue_1.method.message_count
        connection.close()
        return q_1 < MAX_BALANCER_MESSAGE
    except:
        return False
