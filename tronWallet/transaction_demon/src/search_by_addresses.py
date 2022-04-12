import asyncio
import random
import requests
from typing import List, Dict
from src.external_data.database import get_addresses, get_all_transactions_hash
from src.utils import TronAccountAddress
from src.demon import TransactionDemon
from config import network, logger

def _get_key():
    return [
        "8d375175-fa31-490d-a224-63a056adb60b",
        "16c3b7ca-d498-4314-aa1d-a224135faa26",
        "a684fa6d-6893-4928-9f8e-8decd5f034f2"
    ][random.randint(0, 2)]

class AddressesDemon(TransactionDemon):

    @staticmethod
    def get_all_blocks_by_list_addresses(list_addresses: List[TronAccountAddress]) -> List[int]:
        blocks = []
        for address in list_addresses:
            blocks.extend(AddressesDemon.get_all_transactions_block_by_address(address=address))
        return sorted(blocks)

    @staticmethod
    def get_all_transactions_block_by_address(address: TronAccountAddress) -> List[int]:
        headers = {"Accept": "application/json", "TRON-PRO-API-KEY": _get_key()}
        url = f"https://api.{'' if network == 'mainnet' else f'{network.lower()}.'}trongrid.io/v1/accounts/{address}/transactions?limit=200"
        response = requests.get(url, headers=headers).json()
        if "data" in response and len(response["data"]) == 0:
            return []
        return sorted([block["blockNumber"] for block in response["data"]])

    @staticmethod
    def fix_list(list_block: List[int], start_block: int = None, end_block: int = None) -> List[int]:
        blocks = []
        for block in list_block:
            if start_block >= block <= end_block:
                blocks.append(block)
        return blocks

    async def start(
            self, start_block: int = None, end_block: int = None,
            list_addresses: List[TronAccountAddress] = None,  list_blocks: List[int] = None
    ):
        logger.error("The beginning of the search through the list of addresses")
        if list_addresses is None or list_addresses == "all":
            addresses: List = await get_addresses()
        else:
            addresses: List = list_addresses
        logger.error(f"List of addresses: {addresses}")
        list_block = AddressesDemon.get_all_blocks_by_list_addresses(list_addresses=list_addresses)
        if not start_block and not end_block and list_blocks is None:
            logger.error("Search through all blocks")
            await self.start_to_list(
                list_block=list_block,
                list_addresses=addresses
            )
        if not start_block and not end_block and list_blocks is not None:
            logger.error("Search through all blocks")
            await self.start_to_list(list_block=list_blocks, list_addresses=addresses)
        elif not start_block and end_block:
            logger.error(f"Search from 1 block to {end_block} block")
            await self.start_to_list(
                list_block=AddressesDemon.fix_list(list_block=list_block, start_block=1, end_block=end_block),
                list_addresses=addresses
            )
        elif start_block and not end_block:
            logger.error(f"Search from {start_block} block to the last block in the system.")
            await self.start_to_list(
                list_block=AddressesDemon.fix_list(
                    list_block=list_block,
                    start_block=1,
                    end_block=(await self.get_node_block_number())
                ),
                list_addresses=addresses
            )
        else:
            logger.error(f"Search from {start_block} block to {end_block} block")
            await self.start_in_range(start_block=start_block, end_block=end_block, list_addresses=addresses)

    async def start_to_list(self, list_block: List[int], list_addresses: List[TronAccountAddress]):
        for block_number in list_block:
            await self.processing_block(
                block_number=block_number,
                addresses=list_addresses
            )