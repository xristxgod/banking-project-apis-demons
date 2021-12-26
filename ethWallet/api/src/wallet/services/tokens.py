from src.utils.node import NodeETH
import json
from decimal import Decimal
import web3.exceptions
from config import logger


class WalletToken(NodeETH):
    """This class is used to work with the token"""
    def get_token_balance(self, address: str, symbol: str) -> json:
        """
        Get contract(token) balance
        :param address: Wallet address
        :param symbol: Token name
        """
        try:
            address = self.node.toChecksumAddress(address)
        except web3.exceptions.InvalidAddress as error:
            return {"error": str(error)}

        contract = self.get_contract(symbol=symbol.upper())
        if contract and contract is not None:
            try:
                balance_token = int(contract.functions.balanceOf(address).call())
                decimals = int(contract.functions.decimals().call())
            except web3.exceptions.ABIFunctionNotFound as error:
                logger.error(f"STEP 19 ERROR: {error}")
                return {"error": str(error)}
            if float(balance_token) > 0:
                balance_eth = round(self.node.fromWei(balance_token, "ether"), 9)
                balance = round(Decimal(balance_token / 10**decimals), 9)
            else:
                balance_eth = 0
                balance = 0
            logger.error(f"USER '{address}' TOKEN '{symbol.upper()}' BALANCE: {balance}")
            return {
                "balance": str(balance),
                "token": str(symbol.upper()),
                "balanceETH": str(balance_eth)
            }
        else:
            logger.error(f"TOKEN IS NOT IN THE SYSTEM")
            return {
                "message": "This token is not in the system. "
                           "Add it via 'add-token' passing the address of the contract (token) to it."
            }

    def get_all_token(self) -> json:
        """
        Get all files

        :return: Returns all `files` that are in the system
        """
        logger.error(f"GET ALL TOKEN")
        return {
            "files": self.db.get_all_tokens()
        }

    def add_new_token(self, address: str) -> json:
        """
        Add a new token to the "ALL_TOKENS" file
        :param address: Token smart contract address

        :return: If the token was added `True` otherwise `False`
        """
        try:
            address = self.node.toChecksumAddress(address)
        except web3.exceptions.InvalidAddress as error:
            return {"error": str(error)}

        is_valid = self.db.is_token(address=address)

        if not is_valid:
            try:
                contract = self.node.eth.contract(
                    address=address,
                    abi=self.abi
                )
                symbol: str = contract.functions.symbol().call()
                self.db.add_new_token(address=address, symbol=symbol.upper())
                logger.error(f"ADD NEW TOKEN: {symbol}")
                return {
                    "message": f"The token '{symbol}' has been added"
                }
            except web3.exceptions.ABIFunctionNotFound as error:
                logger.error(f"STEP 70 ERROR: {error}")
                return {"error": str(error)}
            except web3.exceptions.ContractLogicError as error:
                logger.error(f"STEP 70 ERROR: {error}")
                return {"error": str(error)}
            except Exception as error:
                logger.error(f"STEP 70 ERROR: {error}")
                return {"error": str(error)}
        else:
            logger.error(f"THE TOKEN '{is_valid}' IS ALREADY IN THE SYSTEM")
            return {"message": f"This token '{is_valid}' is in the system"}


wallet_tokens = WalletToken()
