from flask import Flask, jsonify
from flask_pydantic import validate
from services.get_balance import QueryBalance, get_balance
from services.send_transaction import BodySendTransaction, send_transaction
from services.create_wallet import BodyCreateWallet, create_wallet


app = Flask(__name__)


@app.route('/documentation', methods=['GET'])
def doc():
    """Documentation"""
    return jsonify({'doc': {
        'create_wallet': ['POST', '/create-wallet', BodyCreateWallet.schema()],
        'get_balance': ['GET', '/get-balance', QueryBalance.schema()],
        'send_transaction': ['POST', '/send-transaction', BodySendTransaction.schema()],
    }})


@app.route('/get-balance', methods=['GET'])
@validate()
def route_get_balance(query: QueryBalance):
    return get_balance(query=query)


@app.route('/send-transaction', methods=['POST'])
@validate()
def route_send_transaction(body: BodySendTransaction):
    return send_transaction(body=body)


@app.route('/create-wallet', methods=['POST'])
@validate()
def route_create_wallet(body: BodyCreateWallet):
    return create_wallet(body=body)


if __name__ == '__main__':
    app.run()
