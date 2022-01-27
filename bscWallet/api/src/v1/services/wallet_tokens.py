from fastapi import HTTPException
from starlette import status

from src.utils.node import node_singleton
import json
from decimal import Decimal
import web3.exceptions
from config import logger


class WalletToken:
    """This class is used to work with the token"""
    def __init__(self):
        self.node_bridge = node_singleton

    async def get_balance(self, address: str, symbol: str) -> json:
        """
        Get contract(token) balance
        :param address: Wallet address
        :param symbol: Token name
        """
        try:
            address = self.node_bridge.async_node.toChecksumAddress(address)
        except web3.exceptions.InvalidAddress as error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

        contract = await self.node_bridge.get_contract(symbol=symbol.upper())
        if contract and contract is not None:
            try:
                balance_token = int(contract.functions.balanceOf(address).call())
                decimals = int(contract.functions.decimals().call())
            except web3.exceptions.ABIFunctionNotFound as error:
                logger.error(f"STEP 19 ERROR: {error}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
            if float(balance_token) > 0:
                balance = round(Decimal(balance_token / 10**decimals), 9)
            else:
                balance = 0
            logger.error(f"USER '{address}' TOKEN '{symbol.upper()}' BALANCE: {balance}")
            return {
                "balance": str(balance),
                "token": str(symbol.upper()),
            }
        else:
            logger.error(f"TOKEN IS NOT IN THE SYSTEM")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="This token is not in the system. "
                       "Add it via 'add-token' passing the address of the contract (token) to it."
            )


wallet_tokens = WalletToken()
