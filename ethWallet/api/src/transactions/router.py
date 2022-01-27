from flask import Blueprint, request, jsonify
from .services.ethereum import transaction_ethereum
from .services.tokens import transaction_token
from config import logger


transactions_router = Blueprint('transactions', __name__)


@transactions_router.route("/create-transaction-service", methods=["POST", "GET"])
def create_transaction_with_admin_fee():
    """Create transaction with admin fee and wallet"""
    if request.method == "POST":
        logger.error(f"Calling '/create-transaction'")
        if "fromAddress" not in request.json:
            return jsonify({"error": "The argument 'fromAddress' was not found"})
        if "outputs" not in request.json:
            return jsonify({"error": "The argument 'outputs' was not found"})
        if len(request.json['outputs']) != 1:
            return jsonify({"error": "The argument 'outputs' can contain only one output"})
        if "adminAddress" not in request.json:
            return jsonify({'error': 'The argument "adminAddress" was not found'})
        if "adminFee" not in request.json:
            return jsonify({'error': 'The argument "adminFee" was not found'})

        return jsonify(transaction_ethereum.create_transaction(
            from_address=request.json["fromAddress"],
            outputs=request.json["outputs"],
            gas=2000000 if "gas" not in request.json else request.json["gas"],
            admin_address=request.json['adminAddress'],
            admin_fee=request.json['adminFee']
        ))
    else:
        return jsonify({'error': 'Use a "POST" request'})


@transactions_router.route("/create-transaction", methods=["POST", "GET"])
def create_transaction():
    """Only sign transaction"""
    if request.method == "POST":
        logger.error(f"Calling '/create-transaction'")
        if "fromAddress" not in request.json:
            return jsonify({"error": "The argument 'fromAddress' was not found"})
        if "outputs" not in request.json:
            return jsonify({"error": "The argument 'outputs' was not found"})
        if len(request.json['outputs']) != 1:
            return jsonify({"error": "The argument 'outputs' can contain only one output"})
        return jsonify(transaction_ethereum.create_transaction(
            from_address=request.json["fromAddress"],
            outputs=request.json["outputs"],
            gas=21000 if "gas" not in request.json else request.json["gas"]
        ))
    else:
        return jsonify({'error': 'Use a "POST" request'})


@transactions_router.route("/sign-send-transaction", methods=["POST", "GET"])
def send_transaction():
    """Only send signed transaction"""
    logger.error(f"Calling '/sign-send-transaction'")
    if request.method == "POST":
        if not request.json or "payload" not in request.json:
            return jsonify({"error": "The argument 'createTxHex' was not found"})
        elif "privateKeys" not in request.json:
            return jsonify({"error": "The argument 'privateKeys' was not found"})
        return jsonify(transaction_ethereum.sign_send_transaction(
            payload=request.json["payload"],
            private_keys=request.json['privateKeys']
        ))
    else:
        return jsonify({'error': 'Use a "POST" request'})


@transactions_router.route("/sign-send-token-transaction", methods=["POST", "GET"])
def send_token_transaction():
    """Create, sign and send token transaction"""
    if request.method == "POST":
        logger.error(f"Calling '/sign-send-token-transaction'")
        if not request.json or "payload" not in request.json:
            return jsonify({"error": "The argument 'createTxHex' was not found"})
        elif "privateKeys" not in request.json:
            return jsonify({"error": "The argument 'privateKeys' was not found"})
        return jsonify(transaction_token.sign_send_transaction(
            private_keys=request.json["privateKeys"],
            payload=request.json["payload"]
        ))
    else:
        return jsonify({'error': 'Use a "POST" request'})


@transactions_router.route("/create-token-transaction-service", methods=["POST", "GET"])
def create_token_transaction_with_admin_fee():
    """Only create a token transaction"""
    if request.method == "POST":
        logger.error(f"Calling '/create-token-transaction'")
        if "fromAddress" not in request.json:
            return jsonify({"error": "The argument 'fromAddress' was not found"})
        if "outputs" not in request.json:
            return jsonify({"error": "The argument 'outputs' was not found"})
        if "token" not in request.json:
            return jsonify({"error": "The argument 'token' was not found"})
        if "adminAddress" not in request.json:
            return jsonify({'error': 'The argument "adminAddress" was not found'})
        if "adminFee" not in request.json:
            return jsonify({'error': 'The argument "adminFee" was not found'})

        return jsonify(transaction_token.create_transaction(
            from_address=request.json["fromAddress"],
            outputs=request.json["outputs"],
            gas=2000000 if "gas" not in request.json else request.json["gas"],
            symbol=request.json["token"],
            admin_address=request.json["adminAddress"],
            admin_fee=request.json["adminFee"]
        ))
    else:
        return jsonify({'error': 'Use a "POST" request'})


@transactions_router.route("/create-token-transaction", methods=["POST", "GET"])
def create_token_transaction():
    """Only sign token transaction"""
    if request.method == "POST":
        logger.error(f"Calling '/create-token-transaction'")
        if "fromAddress" not in request.json:
            return jsonify({"error": "The argument 'fromAddress' was not found"})
        if "outputs" not in request.json:
            return jsonify({"error": "The argument 'outputs' was not found"})
        if "token" not in request.json:
            return jsonify({"error": "The argument 'token' was not found"})

        return jsonify(transaction_token.create_transaction(
            from_address=request.json["fromAddress"],
            outputs=request.json["outputs"],
            gas=2000000 if "gas" not in request.json else request.json["gas"],
            symbol=request.json["token"]
        ))
    else:
        return jsonify({'error': 'Use a "POST" request'})


@transactions_router.route("/get-transaction", methods=["POST", "GET"])
def get_transaction():
    """Get transaction"""
    if request.method == "POST":
        logger.error(f"Calling '/get-transaction'")
        if not request.json or "trxHash" not in request.json:
            return jsonify({"error": "The argument 'trxHash' was not found"})
        return jsonify(transaction_ethereum.get_transaction(
            transaction_hash=request.json["txHash"]
        ))
    else:
        return jsonify({'error': 'Use a "POST" request'})


@transactions_router.route("/get-all-transactions", methods=["POST", "GET"])
def get_all_transactions():
    """ Show all transactions by wallet address """
    if request.method == "POST":
        logger.error(f"Calling '/get-all-transactions'")
        if not request.json or "address" not in request.json:
            return jsonify({"error": "The argument 'address' was not found"})
        return jsonify(transaction_ethereum.get_transactions(
            address=request.json['address']),
            direction_to_me=None
        )
    else:
        return jsonify({'error': 'Use a "POST" request!'})


@transactions_router.route("/get-optimal-gas", methods=["POST", "GET"])
def get_optimal_gas():
    """Get optimal gas for transaction"""
    if request.method == "POST":
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
        return jsonify({'error': 'Use a "POST" request!'})
