from solana.publickey import PublicKey
from solana.system_program import TransactionInstruction, Transaction, transfer, TransferParams
from schemas import BodySendTransaction
from clients import solana_api


def __set_transaction(from_pubkey: PublicKey, instruction: TransactionInstruction) -> Transaction:
    transaction = Transaction(
        fee_payer=from_pubkey,
        recent_blockhash=solana_api.client.get_recent_blockhash(),
    )
    transaction.add(instruction)
    return transaction


def __sign_and_send_transaction(transaction: Transaction):
    transaction.sign()
    return solana_api.client.send_transaction(transaction.serialize())


def send_transaction(body: BodySendTransaction):
    to_pubkey = PublicKey(body.to_pubkey)
    from_pubkey = PublicKey(body.from_pubkey)

    instruction = transfer(TransferParams(
        from_pubkey=from_pubkey,
        to_pubkey=to_pubkey,
        lamports=body.lamports
    ))
    transaction = __set_transaction(from_pubkey, instruction)
    signature = __sign_and_send_transaction(transaction)['result']
    return solana_api.client.confirm_transaction(signature)
