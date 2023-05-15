from apps.transaction import schemas


def build_transaction(
        transaction: dict, transaction_type: schemas.TransactionType
) -> schemas.BaseResponseSendTransactionSchema:
    pass
