from typing import List
from datetime import datetime
from config import decimal, Decimal
from src.node import btc
from src.rpc.database import DB


def sign_and_send_transaction(
        create_tx_hex, max_fee_rate: str, admin_fee: str, from_address: str, outputs: List[dict],
) -> dict:
    """
    Sign and send transaction
    :param create_tx_hex: Hex of created transaction
    :type create_tx_hex: str | "sdfg124rtbGv34en6...hdvg1144ktb54e1nx"
    :param max_fee_rate: Reject transactions whose fee rate is higher than the specified value, expressed in BTC/kB.
    :type max_fee_rate: float | str | default=0.10
    :param admin_fee : float | str | fee for service. Just adding to recipients.
    :type from_address: sender's address - using only for building response
    :param from_address : str
    :type outputs: recipients - using only for building response
    :param outputs : List[dict]
    :return:
    """
    balance: Decimal = DB.get_balance(from_address)
    to_address, value = list(outputs[0].items())[0]
    value = decimal.create_decimal(value)
    admin_fee = decimal.create_decimal(admin_fee)

    if balance is None:
        return {"error": 'Wallet is not founded'}
    if balance < value + admin_fee:
        return {"error": 'Not enough balance'}
    try:
        sign_tx_hax = btc.rpc_host.signrawtransactionwithwallet(create_tx_hex)
    except Exception as e:
        return {"error": f'Cant sign: {e}'}
    if type(sign_tx_hax) == bool:
        return {"error": "Can't sign transaction'"}

    try:
        send_trx_hash = btc.rpc_host.send_raw_transaction(
            tx_hex=sign_tx_hax["hex"],
            max_fee_rate=max_fee_rate
        )
    except Exception as e:
        return {"error": f"Can't send transaction: {e}. SIGNED: {sign_tx_hax}"}

    try:
        tx = btc.rpc_host.get_transactions_by_id(send_trx_hash)
        result_tx = formatted_tx(tx, max_fee_rate)

        node_fee = decimal.create_decimal(result_tx['fee'])

        return {
            'time': int(round(datetime.now().timestamp())),
            'fee': "%.8f" % node_fee,
            'transactionHash': tx['hash'],
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
                    'amount': "%.8f" % (value - node_fee)
                }
            ],
        }
    except Exception as e:
        return {'error': f'Cant get transaction after signing: {e}'}


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
