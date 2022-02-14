import os
import uuid
import json
from typing import List, Tuple, Dict

from src.utils import TronAccountAddress
from src.external_data.rabbit_mq import send_message, send_to_balancer
from src.external_data.database import get_all_transactions_hash, get_transaction_hash
from config import ERROR, NOT_SEND, NOT_SEND_TO_TRANSACTION, AdminAddress, ReportingAddress, logger, decimals

AdminsWallets = [AdminAddress, ReportingAddress]

def is_valid(value: dict, string: str):
    func = lambda v, s: True if s in v and len(v[s]) > 0 else False
    return func(v=value, s=string)

def export_transactions(all_transactions: List, addresses: List[TronAccountAddress], block_number: int) -> None:
    """
    Sending packaging in RabbitMQ.
    :param all_transactions: All transactions collected from the block
    :param addresses: Addresses in the system
    :param block_number: Block number
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

def add_into_addresses(addresses: List[TronAccountAddress], all_transactions: List[Dict], block_number: int) -> Tuple:
    """
        Add a transaction to the array for the desired address
        :param addresses: Addresses in the system
        :param all_transactions: All transactions collected from the block
        :param block_number Block number
        """
    # TRX transactions, as well as defrost and freeze balance
    trx_tnx = []
    # TRC20 token transaction only, namely USDT.
    usdt_tnx = []
    # TRC20 token transaction only, namely USDC.
    usdc_tnx = []
    # For the balance transfer script
    balancer_tnx = []
    all_transactions_hash_in_db = get_all_transactions_hash()
    for txn in all_transactions:
        trigger = "TRX"

        is_senders = is_valid(value=txn, string="senders")
        is_recipients = is_valid(value=txn, string="recipients")

        if is_senders and txn["senders"][0]["address"] in [*addresses, *AdminsWallets]:
            address = txn["senders"][0]["address"]
        elif is_recipients and txn["recipients"][0]["address"] in [*addresses, *AdminsWallets]:
            address = txn["recipients"][0]["address"]
        else:
            address = ""

        if address in addresses and is_senders \
                and txn["senders"][0]["address"] in addresses and is_recipients \
                and txn["recipients"][0]["address"] in AdminsWallets:
            continue

        if "transactionType" in txn and txn["transactionType"] == "TriggerSmartContract" and "token" in txn:
            trigger = "USDT" if txn["token"] == "USDT" else "USDC"

        if address not in AdminsWallets and is_senders and txn["senders"][0]["address"] not in AdminsWallets and \
                is_recipients and txn["recipients"][0]["address"] not in AdminsWallets:
            # If the transaction was outside the admin address, and was addressed to the user from the Nth person.
            # We send it to the balancer to withdraw funds from the account.
            balancer_tnx.append({"address": address, "token": trigger})

        if address in AdminsWallets and is_senders and txn["senders"][0]["address"] in AdminsWallets:
            if is_recipients and txn["recipients"][0]["address"] in addresses and trigger == "TRX":
                # If the transaction was sent from the admin to the user's wallet to pay the commission.
                txn = get_transaction_for_fee(transaction=txn)
            elif txn["transactionHash"] in all_transactions_hash_in_db:
                # If the transaction was sent from the admin wallet to another wallet (outside the system).
                txn = get_transaction_in_db(transaction_hash=txn["transactionHash"], transaction=txn)
            address = ReportingAddress

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

def get_transaction_in_db(transaction_hash: str, transaction: Dict) -> Dict:
    """
    If the transaction is in the database, then we adjust it to the standard
    :param transaction_hash: Transaction hash
    :param transaction: The transaction itself
    """
    transaction_in_db = get_transaction_hash(transaction_hash=transaction_hash)
    if transaction_in_db is not None:
        transaction["senders"] = transaction_in_db["from_wallets"]
        transaction["recipients"] = transaction_in_db["to_wallets"]
    return transaction

def get_transaction_for_fee(transaction: Dict) -> Dict:
    """
    If the transaction is a fee payment
    :param transaction: The transaction itself
    """
    amount = decimals.create_decimal(transaction["amount"])
    fee = decimals.create_decimal(transaction["fee"]) if float(transaction["fee"]) > 0 else 0
    from_amount = amount + fee
    return {
        "time": transaction["time"],
        "transactionHash": transaction["transactionHash"],
        "amount": "%.8f" % amount,
        "fee": "%.8f" % fee,
        "recipients": [],
        "senders": [{"address": ReportingAddress, "amount": "%.8f" % from_amount}]
    }

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