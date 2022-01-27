import os
import uuid
import json
from typing import List, Tuple

from src.external_data.rabbit_mq import send_message, send_to_balancer
from src.utils import TronAccountAddress
from config import logger, ERROR, NOT_SEND, AdminAddress, NOT_SEND_TO_TRANSACTION


def export_transactions(all_transactions: List, addresses: List[TronAccountAddress], block_number: int) -> None:
    """
    :param all_transactions:
    :param addresses:
    :param block_number:
    :return:
    """
    ## TRX transactions, as well as defrost and freeze balance
    trx_tnx = []
    # TRC20 token transaction only, namely USDT.
    usdt_tnx = []
    # TRC20 token transaction only, namely USDC.
    usdc_tnx = []
    # For the balance transfer script
    balancer_tnx = []

    transactions: Tuple = add_into_addresses(
        addresses=addresses, all_transactions=all_transactions, block_number=block_number
    )
    trx_tnx, usdt_tnx, usdc_tnx, balancer_tnx = transactions

    if len(trx_tnx) > 1:
        logger.error(f"New TX in Block: {block_number}")
        send_to_rabbit_mq(values=json.dumps(trx_tnx))
    if len(usdt_tnx) > 1:
        logger.error(f"New TRC20 USDT TX in Block: {block_number}")
        send_to_rabbit_mq(values=json.dumps(usdt_tnx))
    if len(usdc_tnx) > 1:
        logger.error(f"New TRC20 USDC TX in Block: {block_number}")
        send_to_rabbit_mq(values=json.dumps(usdc_tnx))
    if balancer_tnx:
        logger.error(f"New TX in balancer: {block_number}")
        send_to_rabbit_mq_balancer(values=json.dumps(balancer_tnx))


def add_into_addresses(addresses: List[TronAccountAddress], all_transactions: List[dict], block_number: int) -> Tuple:
    """
    Add a transaction to the array for the desired address
    :param addresses:
    :param all_transactions:
    :param block_number
    """
    # TRX transactions, as well as defrost and freeze balance
    trx_tnx = []
    # TRC20 token transaction only, namely USDT.
    usdt_tnx = []
    # TRC20 token transaction only, namely USDC.
    usdc_tnx = []
    # For the balance transfer script
    balancer_tnx = []

    for txn in all_transactions:
        trigger = "TRX"
        if "senders" in txn and txn["senders"][0]["address"] in addresses or txn["senders"][0]["address"] == AdminAddress:
            address = txn["senders"][0]["address"]
        elif "recipients" in txn and len(txn["recipients"]) > 0 \
                and txn["recipients"][0]["address"] in addresses \
                or txn["recipients"][0]["address"] == AdminAddress:
            address = txn["recipients"][0]["address"]
        else:
            address = ""
        if "transactionType" in txn and txn["transactionType"] == "TriggerSmartContract" and "token" in txn:
            if txn["token"] == "USDT":
                trigger = "USDT"
            elif txn["token"] == "USDC":
                trigger = "USDC"

        if AdminAddress != address and "senders" in txn and txn["senders"][0]["address"] != AdminAddress \
                and "recipients" in txn and txn["recipients"][0]["address"] != AdminAddress:
            balancer_tnx.append({"address": address, "token": trigger})

        if trigger == "USDT":
            usdt_tnx: List = final_packing(address=address, transaction=txn, list_transactions=usdt_tnx)
        elif trigger == "USDC":
            usdc_tnx: List = final_packing(address=address, transaction=txn, list_transactions=usdc_tnx)
        else:
            trx_tnx: List = final_packing(address=address, transaction=txn, list_transactions=trx_tnx)

    if len(trx_tnx) > 0:
        trx_tnx.insert(0, {"network": "tron", "block": block_number})
    if len(usdt_tnx) > 0:
        usdt_tnx.insert(0, {"network": "tron_trc20_usdt", "block": block_number})
    if len(usdc_tnx) > 0:
        usdc_tnx.insert(0, {"network": "tron_trc20_usdc", "block": block_number})

    return trx_tnx, usdt_tnx, usdc_tnx, balancer_tnx


def final_packing(address: TronAccountAddress, transaction: dict, list_transactions: List) -> List:
    """
    Final packing.
    :param address: Wallet address
    :param transaction: Full transaction
    :param list_transactions: List transactions
    """
    for transactions in list_transactions:
        if address in transactions["address"]:
            transactions["transactions"].append(transaction)
            break
    else:
        list_transactions.append({"address": address, "transactions": [transaction]})
    return list_transactions


def send_to_rabbit_mq(values: json) -> None:
    """
    Send collected data to queue
    :param values: Packaged transactions to send
    """
    try:
        send_message(values=values)
    except Exception as error:
        logger.error(f"fSend to MQ error: {error}")
        with open(ERROR, "a", encoding="utf-8") as file:
            # If an error occurred on the RabbitMQ side, write about it.
            file.write(f"Error Step 187: {values} | RabbitMQ not responding {error} \n")
        new_not_send_file = os.path.join(NOT_SEND, f'{uuid.uuid4()}.json')
        with open(new_not_send_file, 'w') as file:
            # Write all the verified data to a json file, and do not praise the work
            file.write(str(values))


def send_to_rabbit_mq_balancer(values: json) -> None:
    """
        Send collected data to queue
        :param values: Packaged transactions to send
        """
    try:
        send_to_balancer(values=values)
    except Exception as error:
        logger.error(f"fSend to MQ Balancer error: {error}")
        with open(ERROR, "a", encoding="utf-8") as file:
            # If an error occurred on the RabbitMQ side, write about it.
            file.write(f"Error Step 187: {values} | RabbitMQ not responding {error} \n")
        new_not_send_file = os.path.join(NOT_SEND_TO_TRANSACTION, f'{uuid.uuid4()}.json')
        with open(new_not_send_file, 'w') as file:
            # Write all the verified data to a json file, and do not praise the work
            file.write(str(values))


# <<<----------------------------------->>> Send everything that was not sent <<<------------------------------------>>>

def send_all_from_folder_not_send():
    """Send those transits that were not sent due to any errors"""
    files = os.listdir(NOT_SEND)
    for file_name in files:
        try:
            path = os.path.join(NOT_SEND, file_name)
            with open(path, 'r') as file:
                values = file.read()
            send_to_rabbit_mq(values=values)
            os.remove(path)
        except Exception as error:
            logger.error(f"Error: {error}")
            logger.error(f"Not send: {file_name}")
            continue
    files = os.listdir(NOT_SEND_TO_TRANSACTION)
    for file_name in files:
        try:
            path = os.path.join(NOT_SEND, file_name)
            with open(path, 'r') as file:
                values = file.read()
            send_to_rabbit_mq_balancer(values=values)
            os.remove(path)
        except Exception as error:
            logger.error(f"Error: {error}")
            logger.error(f"Not send: {file_name}")
            continue