import json
from typing import Dict

from aiofiles import open as async_open

from src.external_data.database import get_contracts
from src.utils import ContractAddress, to_base58check_address
from config import fileTokens, network, decimals

async def __get_file() -> Dict:
    async with async_open(fileTokens, "r", encoding="utf-8") as file:
        tokens: dict = json.loads(await file.read())
    return tokens

async def get_asset_trc20(address: ContractAddress) -> Dict:
    if network == "shasta" or network == "nile":
        tokens = await __get_file()
    else:
        tokens = get_contracts()
    for token in tokens:
        if address in [token["name"], token["symbol"], token["address"]]:
            return token

async def smart_contract_transaction(data: str, contract_address: ContractAddress) -> Dict:
    """
    Unpacking a smart contract
    :param data: Smart Contract Information
    :param contract_address: Smart contract (Token TRC20) address
    """
    token_dict = await get_asset_trc20(address=contract_address)
    amount = decimals.create_decimal(int("0x" + data[72:], 0) / 10 ** int(token_dict["decimals"]))
    to_address = to_base58check_address("41" + data[32:72])
    token_symbol, token_name = token_dict["symbol"], token_dict["name"]
    return {
        "to_address": to_address,
        "token": token_symbol,
        "name": token_name,
        "amount": "%.8f" % amount
    }