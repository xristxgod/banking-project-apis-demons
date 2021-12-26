import json

from api.src.services.transaction.schemas import (
    BodyCreateTransaction, ResponseCreateTransaction
)
from api.src.node.node import NodeTron

class TRC10Transaction(NodeTron):
    """This class creates, signs and sends TRC10 transactions"""

    def create_transaction(self, body: BodyCreateTransaction) -> ResponseCreateTransaction:
        """Create a transaction TRC10"""
        try:
            # Checks the correctness of the data entered by users
            values = self.examination_transaction(
                fromAddress=body.fromAddress,
                toAddress=body.toAddress,
                amount=body.amount,
                token=body.token
            )
        except Exception as error:
            raise error

        try:
            # Checks whether there are funds on the user's balance for transfer
            if self.node.get_account_asset_balance(addr=values["fromAddress"], token_id=values["token"]) < values["amount"]:
                raise Exception("You don't have enough funds on your balance to transfer!!")
            message = "1.You have about 2-5 minutes to sign and send the order. Otherwise, it will be deleted!!!"
            # Creates a transaction
            create_transaction = self.node.trx.asset_transfer(
                from_=values["fromAddress"],
                to=values["toAddress"],
                amount=values["amount"],
                token_id=values["token"]
            )
            # Receives account resources to generate a commission
            resource = self.node.get_account_resource(addr=values["fromAddress"])
            # If the user does not have enough bandwidth, a fixed transaction fee will be charged
            if "freeNetUsed" in resource and resource["freeNetLimit"] - resource["freeNetUsed"] < 281:
                message += " 2.Your account has run out of bandwidth, from that moment you will be charged a commission" \
                           " for each TRX and TRC10 transaction in the amount of 0.282 TRX. To make transactions free" \
                           " again, freeze silent TRX for 'BANDWIDTH'."
                # Setting a commission for a transaction, in the amount of 0.281 TRX
                create_transaction = create_transaction.fee_limit(281_000)
            # Build a transaction
            create_transaction = create_transaction.build()
            return ResponseCreateTransaction(
                # The original transaction data for signing and sending the transaction
                createTxHex=json.dumps(create_transaction.to_json()["raw_data"]).encode("utf-8").hex(),
                # The body of the transaction, you can find out all the details from it
                bodyTransaction=create_transaction.to_json(),
                message=message
            )
        except Exception as error:
            raise error

transaction_trc10 = TRC10Transaction()

