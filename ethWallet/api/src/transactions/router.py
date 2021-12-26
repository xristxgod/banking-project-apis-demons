from flask import Blueprint, request, jsonify
from .services.ethereum import transaction_ethereum
from .services.tokens import transaction_token
from config import logger


transactions_router = Blueprint('transactions', __name__)


@transactions_router.route("/create-transaction", methods=["POST", "GET"])
def create_transaction():
    """Only sign transaction"""
    if request.method == "POST":
        logger.error(f"Calling '/sign-transaction'")
        if not request.json or "privateKey" not in request.json:
            return jsonify({"error": "The argument 'privateKey' was not found"})
        if "fromAddress" not in request.json:
            return jsonify({"error": "The argument 'fromAddress' was not found"})
        if "toAddress" not in request.json:
            return jsonify({"error": "The argument 'toAddress' was not found"})
        if "amount" not in request.json:
            return jsonify({"error": "The argument 'amount' was not found"})

        return jsonify(transaction_ethereum.create_and_sign_transaction(
            from_address=request.json["fromAddress"],
            from_private_key=request.json["privateKey"],
            to_address=request.json["toAddress"],
            amount=request.json["amount"],
            gas=2000000 if "gas" not in request.json else request.json["gas"]
        ))
    else:
        return jsonify({'error': 'Use a "POST" request'})


@transactions_router.route("/sign-send-transaction", methods=["POST", "GET"])
def send_transaction():
    """Only send signed transaction"""
    logger.error(f"Calling '/send-raw-transaction'")
    if request.method == "POST":
        if not request.json or "createTxHex" not in request.json:
            return jsonify({"error": "The argument 'createTxHex' was not found"})
        return jsonify(transaction_ethereum.send_transaction(
            raw_transaction=request.json["createTxHex"]
        ))
    else:
        return jsonify({'error': 'Use a "POST" request'})


@transactions_router.route("/sign-send-token-transaction", methods=["POST", "GET"])
def send_token_transaction():
    """Create, sign and send token transaction"""
    if request.method == "POST":
        logger.error(f"Calling '/send-token-transaction'")
        if not request.json or "privateKey" not in request.json:
            return jsonify({"error": "The argument 'privateKey' was not found"})
        if "fromAddress" not in request.json:
            return jsonify({"error": "The argument 'fromAddress' was not found"})
        if "toAddress" not in request.json:
            return jsonify({"error": "The argument 'toAddress' was not found"})
        if "amount" not in request.json:
            return jsonify({"error": "The argument 'amount' was not found"})
        if "token" not in request.json:
            return jsonify({"error": "The argument 'token' was not found"})

        return jsonify(transaction_token.send_transaction(
            from_address=request.json["fromAddress"],
            from_private_key=request.json["privateKey"],
            to_address=request.json["toAddress"],
            amount=request.json["amount"],
            gas=40000 if "gas" not in request.json else request.json["gas"],
            symbol=request.json["token"]
        ))
    else:
        return jsonify({'error': 'Use a "POST" request'})


@transactions_router.route("/create-token-transaction", methods=["POST", "GET"])
def sign_token_transaction():
    """Only sign token transaction"""
    if request.method == "POST":
        logger.error(f"Calling '/sign-token-transaction'")
        if not request.json or "privateKey" not in request.json:
            return jsonify({"error": "The argument 'privateKey' was not found"})
        if "fromAddress" not in request.json:
            return jsonify({"error": "The argument 'fromAddress' was not found"})
        if "toAddress" not in request.json:
            return jsonify({"error": "The argument 'toAddress' was not found"})
        if "amount" not in request.json:
            return jsonify({"error": "The argument 'amount' was not found"})
        if "token" not in request.json:
            return jsonify({"error": "The argument 'token' was not found"})

        return jsonify(transaction_token.create_and_sign_transaction(
            from_address=request.json["fromAddress"],
            from_private_key=request.json["privateKey"],
            to_address=request.json["toAddress"],
            amount=request.json["amount"],
            gas=2000000 if "gas" not in request.json else request.json["gas"],
            symbol=request.json["token"]
        ))
    else:
        return jsonify({'error': 'Use a "POST" request'})


@transactions_router.route("/get-transaction", methods=["POST", "GET"])
def get_transaction():
    """Get transaction"""
    if request.method == "GET":
        logger.error(f"Calling '/get-transaction'")
        if not request.json or "trxHash" not in request.json:
            return jsonify({"error": "The argument 'trxHash' was not found"})
        return jsonify(transaction_ethereum.get_transaction(
            transaction_hash=request.json["txHash"]
        ))
    else:
        return jsonify({'error': 'Use a "GET" request'})


@transactions_router.route("/get-all-transactions", methods=["POST", "GET"])
def get_all_transactions():
    """ Show all transactions by wallet address """
    if request.method == "GET":
        logger.error(f"Calling '/get-all-transactions'")
        if not request.json or "address" not in request.json:
            return jsonify({"error": "The argument 'address' was not found"})
        return jsonify(transaction_ethereum.get_transactions(
            address=request.json['address']),
            direction_to_me=None
        )
    else:
        return jsonify({'error': 'Use a "GET" request!'})


@transactions_router.route("/get-optimal-gas", methods=["POST", "GET"])
def get_optimal_gas():
    """Get optimal gas for transaction"""
    if request.method == "GET":
        logger.error(f"Calling '/get-optimal-gas'")
        if not request.json or "fromAddress" not in request.json:
            return jsonify({"error": "The argument 'fromAddress' was not found"})
        if "toAddress" not in request.json:
            return jsonify({"error": "The argument 'toAddress' was not found"})
        if "amount" not in request.json:
            return jsonify({"error": "The argument 'amount' was not found"})

        return jsonify(transaction_ethereum.get_optimal_gas(
            from_address=request.json["fromAddress"],
            to_address=request.json["toAddress"],
            amount=request.json["amount"]
        ))
    else:
        return jsonify({'error': 'Use a "GET" request!'})
