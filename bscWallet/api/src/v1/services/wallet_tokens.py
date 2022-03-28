from fastapi import HTTPException
from starlette import status

from src.utils.es_send import send_error_to_kibana, send_exception_to_kibana
from src.utils.node import node_singleton
import json
from decimal import Decimal
import web3.exceptions


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
            await send_exception_to_kibana(error, 'ERROR GET BALANCE (INVALID ADDRESS)')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

        contract = await self.node_bridge.get_contract(symbol=symbol.upper())
        if contract and contract is not None:
            try:
                balance_token = int(contract.functions.balanceOf(address).call())
                decimals = int(contract.functions.decimals().call())
            except web3.exceptions.ABIFunctionNotFound as error:
                await send_exception_to_kibana(error, 'ERROR GET BALANCE (ABI')
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
            if float(balance_token) > 0:
                balance = round(Decimal(balance_token / 10**decimals), 9)
            else:
                balance = 0
            return {
                "balance": str(balance),
                "token": str(symbol.upper()),
            }
        else:
            await send_error_to_kibana(msg='TOKEN IS NOT IN THE SYSTEM', code=-1)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="This token is not in the system. "
                       "Add it via 'add-token' passing the address of the contract (token) to it."
            )


wallet_tokens = WalletToken()
