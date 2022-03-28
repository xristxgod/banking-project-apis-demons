from json import dumps
from typing import List
from decimal import Decimal
from datetime import datetime
from config import ADMIN_ADDRESS, decimal
from src.node import btc
from src.rpc.es_send import send_exception_to_kibana
from src.services.v2.sign_send_transaction import formatted_tx, get_fee_for_transaction


def create_transaction(outputs: List[dict], admin_fee, from_address: str):
    try:
        to_address, value = list(outputs[0].items())[0]
        value = decimal.create_decimal(value)
        if value < decimal.create_decimal("0.000015"):
            return {"error": f"Output is dust: {value}"}

        unsigned_tx = btc.rpc_host.send(
            outputs, 1, 'economical', None,
            {'add_to_wallet': False, 'change_address': ADMIN_ADDRESS}
        )

        tx = btc.rpc_host.decode_transaction(unsigned_tx['hex'])
        formatted_tx_info = formatted_tx(tx, 0, admin_fee)

        if not isinstance(admin_fee, Decimal):
            admin_fee = decimal.create_decimal(str(admin_fee))

        node_fee, fee_rate = get_fee_for_transaction(
            len(formatted_tx_info['senders']),
            len(formatted_tx_info['recipients']) - 1,
            tx['size']
        )

        return {
            'createTxHex': dumps({
                'data': unsigned_tx['hex'],
                'adminFee': "%.8f" % admin_fee,
                'fromAddress': from_address,
                'outputs': [{from_address: ".8f" % value}]
            }),
            'fee': '%.8f' % node_fee,
            'maxFeeRate': '%.8f' % fee_rate,

            'time': int(round(datetime.now().timestamp())),
            'transactionHash': tx['hash'],
            'amount': "%.8f" % value,
            'senders': [
                {
                    'address': from_address,
                    'amount': "%.8f" % (value + admin_fee)
                }
            ],
            'recipients': [
                {
                    'address': to_address,
                    'amount': "%.8f" % value
                },
                {
                    'address': ADMIN_ADDRESS,
                    'amount': "%.8f" % admin_fee
                },
            ],
        }
    except Exception as e:
        send_exception_to_kibana(e, 'ERROR CREATE TRANSACTION')
        return {'error': str(e)}
