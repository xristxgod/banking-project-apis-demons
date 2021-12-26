from flask import jsonify, Flask
from src.wallet.services.ethereum import wallet_ethereum
from src.transactions import transactions_router
from src.wallet import wallet_router

from config import logger

app = Flask(__name__)

app.register_blueprint(transactions_router, url_prefix='')
app.register_blueprint(wallet_router, url_prefix='')


@app.route("/", methods=["POST", "GET"])
def is_connected():
    """Check connection status"""
    logger.error(f"Calling '/is-connected'")
    status = wallet_ethereum.is_connect
    if status:
        return jsonify({"message": "Connection established"})
    return jsonify({"message": "No connection"})

@app.route("/get-gas-price", methods=["POST", "GET"])
def get_gas_price():
    gas_price = wallet_ethereum.gas_price
    if gas_price:
        logger.error(f"Calling '/get-gas-price' | {gas_price}")
        return jsonify({"gasPrice": str(gas_price)})
    return jsonify({"message": "No connection"})

@app.route("/docs", methods=["POST", "GET"])
def index():
    logger.error(f"Calling '/docs'")
    return jsonify({
        "Check connection status": [
            "GET", "/"
        ],
        "create_wallet": [
            "POST", "/create-wallet", "Description: Create ethereum wallet."
        ],
        "create_deterministic_wallet": [
            "POST", "/create-deterministic-wallet", "Description: Create deterministic ethereum wallet."
        ],
        "get_balance": [
            "GET", "/get-balance", "Description: Returns ethereum balance."
        ],
        "get_token_balance": [
            "GET", "/get-token-balance", "Description: Returns the balance of the token(contract)."
        ],
        "add_token": [
            "POST", "/add-new-token", "Description: Add a new token(contract) if it is not in the system."
        ],
        "get_all_tokens": [
            "GET", "/get-all-files", "Description: Will return all files(contracts)."
        ],

        "create_transaction": [
            "POST", "/sign-transaction", "Description: Will create unsigned ethereum transaction"
        ],
        "sign_send_transaction": [
            "POST", "/sign-send-transaction", "Description: Sign and send ethereum transaction"
        ],

        "create_token_transaction": [
            "POST", "/create-token-transaction",
            "Description: Will create a token transaction"
        ],
        "sign_send_token_transaction": [
            "POST", "/sign-send-token-transaction", "Description: Sign and send token transaction"
        ],

        "get_transaction": [
            "GET", "/get-transaction", "Description: Returns information about the transaction"
        ],
        "get_optimal_gas": [
            "GET", "/get-optimal-gas", "Description: Returns optimal gas"
        ],
        "get_gas_price": [
            "GET", "/get-gas-price", "Description: Will return the gas price"
        ]
    })

if __name__ == '__main__':
    """Start API"""
    app.run(debug=True)
