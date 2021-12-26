import json
import secrets
import string

import tronpy.exceptions

from api.src.node.node import NodeTron
from api.src.utils.tron_typing import TronAccountAddress
from api.src.services.transaction.schemas import ResponseCreateTransaction
from api.src.services.wallet.schemas import (
    BodyCreateWallet, ResponseCreateWallet, ResponseGetBalance,
    BodyFreezeBalance, BodyUnfreezeBalance, ResponseGetAllTokens
)

class TRXWallet(NodeTron):
    """This class creates and use a Tron account"""

    def create_wallet(self, body: BodyCreateWallet) -> ResponseCreateWallet:
        """Create a tron wallet"""
        if body.passphrase is None:
            # Creating a secret word for the wallet
            passphrase = "".join(secrets.choice(string.ascii_letters + string.digits) for i in range(20))
        else:
            # If the user has entered it, then we leave it
            passphrase = body.passphrase

        try:
            # Generating a wallet
            __wallet = self.node.get_address_from_passphrase(passphrase=passphrase)
        except tronpy.exceptions.BadKey as error:
            raise Exception("This secret word does not fit. Try something else.")

        return ResponseCreateWallet(
            passphrase=passphrase,
            privateKey=__wallet["private_key"],
            publicKey=__wallet["public_key"],
            address=__wallet["base58check_address"],
        )

    def get_balance(self, address: TronAccountAddress) -> ResponseGetBalance:
        """Get TRX balance"""
        if not self.node.is_address(address):
            raise Exception(f"This address '{address}' was not found in the Tron system.")
        try:
            balance = self.node.get_account_balance(addr=address)
        except Exception as error:
            raise error
        return ResponseGetBalance(balance=str(balance), token="TRX")

    # <<<------------------------------------>>> Account info <<<---------------------------------------------------->>>

    def get_account_resource(self, address: TronAccountAddress) -> dict:
        """
        Get resource info of an account

        :return
            freeNetUsed - Free bandwidth used
            freeNetLimit - Total free bandwidth
            NetUsed - Used amount of bandwidth obtained by staking
            NetLimit - 	Total bandwidth obtained by staking
            TotalNetLimit - Total bandwidth can be obtained by staking
            TotalNetWeight - Total TRX staked for bandwidth
            tronPowerLimit - TRON Power(vote)
            EnergyUsed - Energy used
            EnergyLimit - Total energy obtained by staking
            TotalEnergyLimit - Total energy can be obtained by staking
            TotalEnergyWeight - Total TRX staked for energy
        """
        if not self.node.is_address(address):
            raise Exception(f"This address '{address}' was not found in the Tron system.")
        return self.node.get_account_resource(addr=address)

    def get_unspent_energy_by_address(self, address: TronAccountAddress) -> dict:
        """Get the rest of the energy"""
        if not self.node.is_address(address):
            raise Exception(f"This address '{address}' was not found in the Tron system.")

        resource = self.node.get_account_resource(addr=address)

        if "EnergyLimit" in resource and "EnergyUsed" in resource:
            return {
                "unspentEnergy": int(resource["EnergyLimit"]) - int(resource["EnergyUsed"]),
                "energyLimit": int(resource["EnergyLimit"]),
                "energyUsed": int(resource["EnergyUsed"])
            }
        elif "EnergyLimit" in resource and "EnergyUsed" not in resource:
            return {
                "unspentEnergy": int(resource["EnergyLimit"]),
                "energyLimit": int(resource["EnergyLimit"]),
                "energyUsed": 0
            }
        else:
            return {
                "unspentEnergy": 0,
                "energyLimit": 0,
                "energyUsed": 0
            }

    def get_unspent_bandwidth_by_address(self, address: TronAccountAddress) -> dict:
        """Get the unspent bandwidth"""
        if not self.node.is_address(address):
            raise Exception(f"This address '{address}' was not found in the Tron system.")

        resource = self.node.get_account_resource(addr=address)

        if "freeNetLimit" in resource and "freeNetUsed" in resource:
            return {
                "unspentBandwidth": int(resource["freeNetLimit"]) - int(resource["freeNetUsed"]),
                "bandwidthLimit": resource["freeNetLimit"],
                "bandwidthUsed": resource["freeNetUsed"]
            }
        elif "freeNetLimit" in resource and "freeNetUsed" not in resource:
            return {
                "unspentBandwidth": int(resource["freeNetLimit"]),
                "bandwidthLimit": resource["freeNetLimit"],
                "bandwidthUsed": 0
            }
        else:
            return {
                "unspentBandwidth": 0,
                "bandwidthLimit": 0,
                "bandwidthUsed": 0
            }

    # <<<-------------------------------->>> Freeze and Unfreeze account <<<----------------------------------------->>>

    def create_freeze_balance(self, body: BodyFreezeBalance) -> ResponseCreateTransaction:
        """Create a freeze balance"""
        try:
            values: dict = self.examination_transaction(
                fromAddress=body.ownerAddress,
                toAddress=body.toAddress if body.toAddress is not None else body.ownerAddress,
                amount=body.amount
            )
        except Exception as error:
            raise error

        try:
            # Checks whether the user has enough TRX to freeze.
            if self.toSun(self.node.get_account_balance(body.ownerAddress)) < values["amount"]:
                raise Exception("You don't have enough funds to freeze!!")
            # Creates a freeze
            create_freeze = self.node.trx.freeze_balance(
                owner=values["fromAddress"],
                amount=values["amount"],
                resource=body.resource,
                # If the user specified a freeze for another account
                receiver=values["toAddress"] if values["toAddress"] != values["fromAddress"] else None
            ).build()
            return ResponseCreateTransaction(
                createTxHex=json.dumps(create_freeze.to_json()["raw_data"]).encode("utf-8").hex(),
                bodyTransaction=create_freeze.to_json()
            )
        except Exception as error:
            raise error

    def create_unfreeze_balance(self, body: BodyUnfreezeBalance) -> ResponseCreateTransaction:
        """Create a unfreeze balance"""
        try:
            values: dict = self.examination_transaction(
                fromAddress=body.ownerAddress,
                toAddress=body.toAddress if body.toAddress is not None else body.ownerAddress,
            )
        except Exception as error:
            raise error

        try:
            create_unfreeze = self.node.trx.unfreeze_balance(
                owner=values["fromAddress"],
                resource=body.resource,
                # If the user specified defrosting for another account
                receiver=values["toAddress"] if values["toAddress"] != values["fromAddress"] else None
            ).build()
            return ResponseCreateTransaction(
                createTxHex=json.dumps(create_unfreeze.to_json()["raw_data"]).encode("utf-8").hex(),
                bodyTransaction=create_unfreeze.to_json()
            )
        except Exception as error:
            raise error

    # <<<---------------------------------------->>> Others <<<------------------------------------------------------>>>

    def get_all_tokens(self) -> ResponseGetAllTokens:
        """Returns all TRC10 and TRC20 files that are in the system"""
        return ResponseGetAllTokens(
            tokensTRC20=self.trc20_db.get_all_tokens_only_symbol(),
            tokensTRC10=self.trc10_db.get_all_tokens_only_symbol()
        )

trx_wallet = TRXWallet()