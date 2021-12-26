from flask import Blueprint, request, jsonify
from .services.tokens import wallet_tokens
from .services.ethereum import wallet_ethereum
from config import logger


wallet_router = Blueprint('wallet', __name__)


@wallet_router.route("/create-wallet", methods=["POST", "GET"])
def create_wallet():
    """ This method creates an ether wallet """
    if request.method == "POST":
        logger.error(f"Calling '/create-wallet'")
        if not request.json or "words" not in request.json:
            return jsonify(wallet_ethereum.create_wallet())
        return jsonify(wallet_ethereum.create_wallet(request.json['words']))
    else:
        return jsonify({'error': 'Use "POST" request!'})


@wallet_router.route("/create-deterministic-wallet", methods=["POST", "GET"])
def create_deterministic_wallet():
    """ This method creates an ether wallet """
    if request.method == "POST":
        logger.error(f"Calling '/create-deterministic-wallet'")
        if not request.json:
            return jsonify(wallet_ethereum.create_deterministic_wallet())
        if "child" not in request.json:
            child = 10
        else:
            child = request.json["child"]
        if "words" in request.json:
            return jsonify(wallet_ethereum.create_deterministic_wallet(
                words=request.json["words"],
                child=child
            ))
        return jsonify(wallet_ethereum.create_deterministic_wallet(
            child=request.json["child"]
        ))

    else:
        return jsonify({'error': 'Use "POST" request!'})


@wallet_router.route("/get-balance", methods=["POST", "GET"])
def get_balance():
    """ Show Ether balance at wallet address """
    if request.method == "GET":
        logger.error(f"Calling '/get-balance'")
        if not request.json or "address" not in request.json:
            return jsonify({"error": "The argument 'address' was not found"})
        return jsonify(wallet_ethereum.get_balance(address=request.json['address']))
    else:
        return jsonify({'error': 'Use a "GET" request!'})


@wallet_router.route("/get-token-balance", methods=["POST", "GET"])
def get_token_balance():
    """Get token balance"""
    if request.method == "GET":
        logger.error(f"Calling 'get-token-balance'")
        if not request.json or "address" not in request.json:
            return jsonify({"error": "The argument 'address' was not found"})
        if "token" not in request.json:
            return jsonify({"error": "The argument 'token' was not found"})
        return jsonify(wallet_tokens.get_token_balance(
            address=request.json["address"],
            symbol=request.json["token"]
        ))
    else:
        return jsonify({'error': 'Use a "GET" request!'})


@wallet_router.route("/add-new-token", methods=["POST", "GET"])
def add_token():
    """Add new token"""
    if request.method == "POST":
        logger.error(f"Calling '/add-token'")
        if not request.json or "address" not in request.json:
            return jsonify({"error": "The argument 'address' was not found"})
        return jsonify(wallet_tokens.add_new_token(
            address=request.json["address"]
        ))
    else:
        return jsonify({'error': 'Use a "POST" request'})


@wallet_router.route("/get-all-tokens", methods=["POST", "GET"])
def get_all_token():
    """Get all files"""
    if request.method == "GET":
        logger.error(f"Calling '/get-all-token'")
        return jsonify(wallet_tokens.get_all_token())
    else:
        return jsonify({'error': 'Use a "GET" request'})
