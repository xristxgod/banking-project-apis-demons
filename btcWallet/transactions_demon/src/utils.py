from datetime import datetime
from .external_data.database import DB


def convert_time(t: int) -> str:
    return datetime.fromtimestamp(int(t)).strftime('%d-%m-%Y %H:%M:%S')


def get_transaction_in_db(transaction_hash: str, transaction: dict) -> dict:
    transaction_in_db = DB.get_transaction_by_hash(transaction_hash=transaction_hash)
    if transaction_in_db is None:
        return transaction
    transaction["senders"] = transaction_in_db[2]
    transaction["recipients"] = transaction_in_db[3]
    return transaction
