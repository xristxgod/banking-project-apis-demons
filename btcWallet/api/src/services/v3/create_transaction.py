from json import dumps
from typing import List
from datetime import datetime
from config import ADMIN_ADDRESS, decimal
from src.node import btc
from src.rpc.es_send import send_exception_to_kibana
from src.services.v3.sign_send_transaction import get_fee_for_transaction, formatted_tx


def create_transaction(outputs: List[dict], from_address: str):
    try:
        to_address, value = list(outputs[0].items())[0]
        value = decimal.create_decimal(value)
        if value < decimal.create_decimal("0.000015"):
            return {"error": f"Output is dust: {value}"}

        unsigned_tx = btc.rpc_host.send(
            outputs, 1, 'economical', None,
            {
                'add_to_wallet': False,
                'change_address': ADMIN_ADDRESS,
                'change_position': 0,
                'subtract_fee_from_outputs': [0]
            }
        )

        tx = btc.rpc_host.decode_transaction(unsigned_tx['hex'])
        formatted_tx_info = formatted_tx(tx, 0)

        node_fee, fee_rate = get_fee_for_transaction(
            len(formatted_tx_info['senders']),
            len(formatted_tx_info['recipients']),
            tx['size']
        )
        node_fee *= decimal.create_decimal('0.75')
        fee_rate *= decimal.create_decimal('1.25')
        # sent_sum = sum([decimal.create_decimal(x['amount']) for x in formatted_tx_info['senders']])
        #
        # if len(formatted_tx_info['recipients']) > 1:
        #     sent_sum -= decimal.create_decimal(formatted_tx_info['recipients'][0]['amount'])

        return {
            'createTxHex': dumps({
                'data': unsigned_tx['hex'],
                'fromAddress': from_address,
                'outputs': [{to_address: "%.8f" % value}]
            }),
            'fee': '%.8f' % node_fee,
            'maxFeeRate': '%.8f' % fee_rate,
            # 'time': int(round(datetime.now().timestamp())),
            # 'transactionHash': tx['hash'],
            # 'amount': "%.8f" % value,
            # 'senders': [
            #     {
            #         'address': from_address,
            #         'amount': "%.8f" % value
            #     }
            # ],
            # 'recipients': [
            #     {
            #         'address': to_address,
            #         'amount': "%.8f" % (sent_sum - node_fee)
            #     }
            # ],
        }
    except Exception as e:
        send_exception_to_kibana(e, 'ERROR CREATE TRANSACTION')
        return {'error': str(e)}
