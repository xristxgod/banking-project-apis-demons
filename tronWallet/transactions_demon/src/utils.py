import os
import uuid
import json
from datetime import datetime
from typing import List

from .tron_typing import TronAccountAddress
from .external_data.rabbit_mq import send_message
from transactions_demon.config import logger, ERROR, NOT_SEND

def convert_time(t: int) -> str:
    return datetime.fromtimestamp(int(t)).strftime('%d-%m-%Y %H:%M:%S')

def add_into_addresses(addresses: List[TronAccountAddress], funded_trx_for_sending: List[dict]) -> List:
    """
    Add a transaction to the array for the desired address
    :param addresses:
    :param funded_trx_for_sending:
    """
    transactions = []
    for txn in funded_trx_for_sending:
        if txn["senders"] in addresses:
            address = txn["senders"]
        elif txn["transactionType"] == "TriggerSmartContract" \
                and "toAddress" in txn["smartContract"] \
                and txn["smartContract"]["toAddress"] in addresses:
            address = txn["smartContract"]["toAddress"]
        elif txn["transactionType"] in ["TransferContract", "TransferAssetContract"] \
                and txn["recipients"] in addresses:
            address = txn["recipients"]

        elif txn["transactionType"] in ["FreezeBalanceContract", "UnfreezeBalanceContract"] \
                and "recipients" in txn \
                and txn["recipients"] in addresses:
            address = txn["recipients"]
        else:
            address = ''

        transactions: List = final_packing(
            address=address, transaction=txn, list_transactions=transactions
        )
    return transactions

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

def send_to_rabbit_mq(values: json):
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
            file.write(f"Error: {values} | RabbitMQ not responding {error} \n")
        new_not_send_file = os.path.join(NOT_SEND, f'{uuid.uuid4()}.json')
        with open(new_not_send_file, 'w') as file:
            # Write all the verified data to a json file, and do not praise the work
            file.write(str(values))

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