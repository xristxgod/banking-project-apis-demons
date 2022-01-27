from src.node import btc
from typing import List
from config import ADMIN_ADDRESS
from src.services.v2.sign_send_transaction import formatted_tx, get_fee_for_transaction


def create_transaction(outputs: List[dict], admin_fee):
    unsigned_tx = btc.rpc_host.send(
        outputs, 1, 'economical', None,
        {'add_to_wallet': False, 'change_address': ADMIN_ADDRESS}
    )

    decoded_tx = btc.rpc_host.decode_transaction(unsigned_tx['hex'])
    formatted_tx_info = formatted_tx(decoded_tx, 0, admin_fee)

    fee, fee_rate = get_fee_for_transaction(
        len(formatted_tx_info['senders']),
        len(formatted_tx_info['recipients']) - 1,
        decoded_tx['size']
    )
    formatted_tx_info.update({
        'fee': '%.8f' % fee,
        'maxFeeRate': '%.8f' % fee_rate
    })

    return {
        'createTxHex': unsigned_tx['hex'],
        **formatted_tx_info,
    }
