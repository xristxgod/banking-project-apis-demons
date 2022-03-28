from typing import List
from datetime import datetime
from config import decimal, Decimal
from src.node import btc
from src.rpc.database import DB
from src.rpc.es_send import send_exception_to_kibana, send_error_to_kibana


def sign_and_send_transaction(
        create_tx_hex, max_fee_rate: str, from_address: str, outputs: List[dict],
) -> dict:
    """
    Sign and send transaction
    :param create_tx_hex: Hex of created transaction
    :type create_tx_hex: str | "sdfg124rtbGv34en6...hdvg1144ktb54e1nx"
    :param max_fee_rate: Reject transactions whose fee rate is higher than the specified value, expressed in BTC/kB.
    :type max_fee_rate: float | str | default=0.10
    :type from_address: sender's address - using only for building response
    :param from_address : str
    :type outputs: recipients - using only for building response
    :param outputs : List[dict]
    :return:
    """
    balance: Decimal = DB.get_balance(from_address)
    to_address, value = list(outputs[0].items())[0]
    value = decimal.create_decimal(value)

    if balance is None:
        send_error_to_kibana(msg="Wallet is not founded", code=-1)
        return {"error": 'Wallet is not founded'}
    if balance < value:
        send_error_to_kibana(msg="Not enough balance", code=-1)
        return {"error": 'Not enough balance'}
    try:
        sign_tx_hax = btc.rpc_host.signrawtransactionwithwallet(create_tx_hex)
    except Exception as e:
        send_exception_to_kibana(e, f"Can't sign transaction.")
        return {"error": f'Cant sign: {e}'}
    if type(sign_tx_hax) == bool:
        send_error_to_kibana(msg="Can't sign", code=-1)
        return {"error": "Can't sign'"}

    try:
        send_trx_hash = btc.rpc_host.send_raw_transaction(
            tx_hex=sign_tx_hax["hex"],
            max_fee_rate=max_fee_rate
        )
    except Exception as e:
        send_exception_to_kibana(e, "Can't send transaction: {e}. SIGNED: {sign_tx_hax}")
        return {"error": f"Can't send transaction: {e}. SIGNED: {sign_tx_hax}"}

    try:
        tx = btc.rpc_host.get_transactions_by_id(send_trx_hash)
        result_tx = formatted_tx(tx, max_fee_rate)
        sent_sum = sum([decimal.create_decimal(x['amount']) for x in result_tx['senders']])

        if len(result_tx['recipients']) > 1:
            sent_sum -= decimal.create_decimal(result_tx['recipients'][0]['amount'])

        node_fee = (
            sum([decimal.create_decimal(x['amount']) for x in result_tx['senders']])
            - sum([decimal.create_decimal(x['amount']) for x in result_tx['recipients']])
        )

        return {
            'time': int(round(datetime.now().timestamp())),
            'fee': "%.8f" % node_fee,
            'transactionHash': tx['txid'],
            'amount': "%.8f" % value,
            'senders': [
                {
                    'address': from_address,
                    'amount': "%.8f" % value
                }
            ],
            'recipients': [
                {
                    'address': to_address,
                    'amount': "%.8f" % (sent_sum - node_fee)
                }
            ],
        }
    except Exception as e:
        send_exception_to_kibana(e, 'Cant get transaction after signing')


def formatted_tx(tx, max_fee_rate):
    senders, amount = btc.get_senders(tx['vin'])
    recipients, _ = btc.get_recipients(tx['vout'])
    fee = (
        decimal.create_decimal(max_fee_rate)
        * decimal.create_decimal(tx['size'])
        / decimal.create_decimal(1000)
    )

    return {
        "time": None,
        "datetime": None,
        "transactionHash": tx['hash'],
        "amount": "%.8f" % amount,
        "fee": "%.8f" % fee,
        "senders": senders,
        "recipients": recipients
    }


def get_fee_for_transaction(inputs: int, outputs: int, size: int) -> (Decimal, Decimal):
    """
    :param inputs: number of senders.
    :param outputs: number of receivers.
    :param size: size of transaction.
    :return: Tuple(transactions' fee, max fee rate in BTC/KB)
    """
    fees = btc.get_optimal_fees(from_=inputs, to_=outputs, to_confirm_within=1)
    return (
        decimal.create_decimal(fees['BTC/BYTE']) * decimal.create_decimal(size),
        decimal.create_decimal(fees['BTC/KB'])
    )
