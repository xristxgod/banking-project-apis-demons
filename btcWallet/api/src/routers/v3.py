from flask import Blueprint, request, jsonify
from json import loads

from ..rpc.es_send import send_msg_to_kibana
from ..services.v2.create_wallet import create_sub_wallet
from ..services.v3.create_transaction import create_transaction
from ..services.v3.sign_send_transaction import sign_and_send_transaction
from config import ADMIN_ADDRESS
from ..utils import get_status


v3_router = Blueprint('v3', __name__)


@v3_router.route('/btc/create-wallet', methods=['POST', 'GET'])
def create_wallet_by_private_key_route():
    """ This method creates a BTC wallet """
    if request.method == 'POST':
        return jsonify(create_sub_wallet())
    else:
        return jsonify({'error': 'Use a "POST" request'})


@v3_router.route('/btc/create-transaction', methods=['POST', 'GET'])
def create_transaction_route():
    """Create transaction without sign, but with fee"""
    if request.method == 'POST':
        if "outputs" not in request.json:
            return jsonify({'error': 'The argument "outputs" was not found'})

        returned = create_transaction(
            outputs=request.json['outputs'],
            from_address=request.json['fromAddress'] if 'fromAddress' in request.json else ADMIN_ADDRESS
        )
        send_msg_to_kibana(msg=f'CREATE TRANSACTION: {returned}')
        return jsonify(returned), get_status(returned)
    else:
        return jsonify({'error': 'Use a "POST" request'})


@v3_router.route('/btc/sign-send-transaction', methods=['POST', 'GET'])
def sign_and_send_transaction_route():
    """Sign and send a transaction"""
    if request.method == 'POST':
        if not request.json or "createTxHex" not in request.json:
            return jsonify({'error': 'The argument "createTxHex" was not found'})
        if "maxFeeRate" not in request.json:
            return jsonify({'error': 'The argument "maxFeeRate" was not found'})

        payload = loads(request.json['createTxHex'])
        if "outputs" not in payload:
            return jsonify({
                'error': 'The argument "outputs" was not found in createTxHex. Create tx with /v2/btc again'
            })

        tx = sign_and_send_transaction(
            create_tx_hex=payload["data"],
            max_fee_rate=request.json["maxFeeRate"],
            from_address=payload['fromAddress'] if 'fromAddress' in payload else ADMIN_ADDRESS,
            outputs=payload['outputs']
        )
        send_msg_to_kibana(msg=f'SENT TRANSACTION: {tx}')
        return jsonify(tx), get_status(tx)
    else:
        return jsonify({'error': 'Use a "POST" request'})
