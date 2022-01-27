import json
from typing import Optional

import tronpy.exceptions

from ..schemas import ResponseCreateTransaction, BodyCreateTransaction
from src.utils.station import tron_station, get_energy
from src.utils.node import NodeTron
from src.utils.types import TokenTRC20, TronAccountAddress

from config import decimals

class CreateTransaction(NodeTron):
    """This class creates TRX & TRC20 & Freeze & Unfreeze transactions"""
    defaultBDTRX = 267

    # <<<-------------------------------->>> Optimal Fee <<<--------------------------------------------------------->>>

    def get_optimal_fee(self, from_address: TronAccountAddress, to_address: TronAccountAddress, token: Optional[TokenTRC20] = None) -> json:
        """Get optimal fee"""
        fee = 0
        energy = 0
        if token is None:
            try:
                # If an account is not created, an activation fee will be applied
                _ = self.node.get_account(to_address)
            except tronpy.exceptions.AddressNotFound as error:
                fee += 1.0
            bd = self.defaultBDTRX
        else:
            token_dict = self.db.get_token(token=token)
            # Connecting to a smart contract
            contract = self.node.get_contract(addr=token_dict["address"])
            if float(contract.functions.balanceOf(to_address)) > 0:
                energy = token_dict["isBalanceNotNullEnergy"]
            else:
                energy = token_dict["isBalanceNullEnergy"]
            fee = get_energy(address=from_address, energy=energy) / tron_station.calculate_burn_energy(1)
            bd = token_dict["bandwidth"]
        if int(tron_station.get_account_bandwidth(address=from_address)["totalBandwidth"]) <= bd:
            fee += decimals.create_decimal(self.defaultBDTRX) / 1_000
        return {
            "fee": "%.8f" % fee if fee > 0 else fee,
            "energy": energy,
            "bandwidth": bd
        }

    # <<<-------------------------------->>> TRX <<<----------------------------------------------------------------->>>

    def create_transaction(self, body: BodyCreateTransaction) -> ResponseCreateTransaction:
        """Create a transaction TRX"""
        max_fee_rate = 0
        if isinstance(body.outputs, str):
            body.outputs = json.loads(body.outputs)
        address, amount = list(body.outputs[0].items())[0]
        # Checks the correctness of the data entered by users
        val: dict = self.examination_transaction(fromAddress=body.fromAddress, toAddress=address, amount=amount)
        # Resources that will go to the transaction
        resources = self.get_optimal_fee(from_address=val["fromAddress"], to_address=val["toAddress"])
        # Creates and build a transaction
        txn = self.node.trx.transfer(from_=val["fromAddress"], to=val["toAddress"], amount=val["amount"]).build()
        if float(resources["fee"]) > 0:
            max_fee_rate = "%.8f" % (decimals.create_decimal(resources["fee"]) * 2)
        return ResponseCreateTransaction(
            # The original transaction data for signing and sending the transaction
            createTxHex=json.dumps(txn.to_json()["raw_data"]).encode("utf-8").hex(),
            # The body of the transaction, you can find out all the details from it
            bodyTransaction=txn.to_json(),
            # Transaction fee
            fee=resources["fee"],
            # Energy cost per transaction.
            energy=resources["energy"],
            # Bandwidth cost per transaction.
            bandwidth=resources["bandwidth"],
            # The maximum allowable commission per transaction
            maxFeeRate=max_fee_rate
        )

    # <<<-------------------------------->>> TRC 20 <<<-------------------------------------------------------------->>>

    def create_trc20_transactions(self, body: BodyCreateTransaction, token: TokenTRC20) -> ResponseCreateTransaction:
        """Create a transaction TRC20"""
        if isinstance(body.outputs, str):
            body.outputs = json.loads(body.outputs)
        address, amount = list(body.outputs[0].items())[0]
        # Checks the correctness of the data entered by users
        val: dict = self.examination_transaction(fromAddress=body.fromAddress, toAddress=address)
        # Token information
        token_dict = self.db.get_token(token=token)
        # Connecting to a smart contract
        contract = self.node.get_contract(addr=token_dict["address"])
        # Let's get the amount for the offspring in decimal
        amount = int(decimals.create_decimal(amount) * 10 ** int(token_dict["decimal"]))
        # Checks whether the user has a tokens balance to transfer
        if contract.functions.balanceOf(val["fromAddress"]) * 10 ** int(token_dict["decimal"]) < amount:
            raise Exception("You do not have enough funds on your balance to make a transaction!!!")
        resources = self.get_optimal_fee(from_address=val["fromAddress"], to_address=val["toAddress"], token=token)
        # Creating a transaction
        txn = contract.functions.transfer(val["toAddress"], amount).with_owner(val["fromAddress"]).build()
        return ResponseCreateTransaction(
            # The original transaction data for signing and sending the transaction
            createTxHex=json.dumps(txn.to_json()["raw_data"]).encode("utf-8").hex(),
            # The body of the transaction, you can find out all the details from it
            bodyTransaction=txn.to_json(),
            # Transaction fee
            fee=resources["fee"],
            # Energy cost per transaction.
            energy=resources["energy"],
            # Bandwidth cost per transaction.
            bandwidth=resources["bandwidth"],
            # The maximum allowable commission per transaction
            maxFeeRate=token_dict["feeLimit"]
        )

create_transaction = CreateTransaction()