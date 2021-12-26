import asyncio
from typing import Optional, Set
from aiofiles import open as async_open
from aiohttp import web, ClientSession, CookieJar
from database import DB
from rabbit_mq import RabbitMQ
from config import logger, time_str_from_timestamp, SOLANA_URL, LAST_BLOCK_LOG, ERROR
from solana.rpc.async_api import AsyncClient, PublicKey
from os.path import isfile


# Init new event loop for async app
loop = asyncio.new_event_loop()

# Web application for adding new wallets in demon and checking transaction's history
app = web.Application()


class TransactionDemon:
    # Index for numerating transactions in main groups
    FIRST_GROUP_ID = 1
    # Index for user's transactions adding from inside
    NEW_GROUP_ID = 0

    def __init__(self):
        # Aiohttp session
        self.__session: Optional[ClientSession] = None
        # RabbitMQ and DB connections
        self.__rabbit_mq = RabbitMQ()
        self.__db = DB()

    async def __get_current_block(self) -> Optional[int]:
        last_block_response = await self.__session.post(f'https://{SOLANA_URL}', json={
            "jsonrpc": "2.0", "id": 1, "method": "getBlockHeight",
        })
        if not last_block_response.ok:
            return
        return (await last_block_response.json())['result']

    async def start_demon_parser_of_network(self):
        # Connecting to RabbitMQ and DB
        is_run = await self.__init()
        # If it's not running - exit with error
        if not is_run:
            return
        # If we have file with last processed block - then read number of this block
        if isfile(LAST_BLOCK_LOG):
            async with async_open(LAST_BLOCK_LOG, 'r') as f:
                file_data = await f.read()
        else:
            # Else - create empty file for this
            async with async_open(LAST_BLOCK_LOG, 'w'):
                pass
            file_data = ''
        # File exist, not empty and there is number of last block?
        if file_data.isdigit():
            # Then convert to digit
            last_not_processed_block = int(file_data)
        else:
            # Else - just get last block in Solana
            last_not_processed_block = await self.__get_current_block()
        # Start infinity loop for monitoring transactions
        while True:
            # Waiting, for getting bigger pack of block for processing
            await asyncio.sleep(2)
            # Get number of current block in system
            current = await self.__get_current_block()

            # If size of pack not enough - wait and try to get bigger size
            if current - last_not_processed_block < 10:
                continue

            # Getting set of all public keys
            pub_keys = set(await self.__db.get_pub_keys())

            # Getting and processing block in range [last_not_processed_block, current]
            await self.get_transactions_in_blocks_range(
                last_not_processed_block, current, pub_keys=pub_keys
            )
            # Async writing to file next for last processing block
            async with async_open(LAST_BLOCK_LOG, 'w') as f:
                last_not_processed_block = current + 1
                await f.write(f'{last_not_processed_block}')

    async def get_transactions_in_blocks_range(
        self, start: int, end: Optional[int] = None,
        *, pub_keys: Optional[Set[str]] = None
    ):
        """
        It's method for scrypt in `search_in_history_script.py`. Running with params
        :param start: starting slot for searching transactions
        :param end: last slot for searching transactions
        :param pub_keys: set of public keys of our wallets. We are looking for transactions from this list
        :return: bool. True, if all blocks from range was sending to RabbitMQ
        """
        if pub_keys is None:
            pub_keys = set(await self.__db.get_pub_keys())

        # Get blocks from Solana in range [start, end]
        response_blocks = await self.__session.post(f'https://{SOLANA_URL}', json={
            "jsonrpc": "2.0", "id": 1, "method": "getBlocks",
            "params": list(filter(lambda x: x is not None, [start, end]))
        })
        # If it's okay - then continue
        if not response_blocks.ok:
            logger.error(f'Request to {SOLANA_URL} is not OK')
            return False
        blocks_json = (await response_blocks.json())
        # Result exists?
        if blocks_json.get('result') is None:
            logger.error(f'Response is None')
            return False
        # Async processing all blocks in range
        blocks_processed = await asyncio.gather(*[
            self.__check_block_and_send_to_rabbit_mq(block, pub_keys)
            for block in blocks_json['result']
        ])
        # Writing slots with errors to file
        async with async_open(ERROR, 'a') as f:
            for block_number, result in zip(blocks_json['result'], blocks_processed):
                if not result:
                    await f.write(f'{block_number} ')
        return all(blocks_json['result'])

    async def __check_block_and_send_to_rabbit_mq(self, block: int, pub_keys: Set[str]):
        """
        Method for checking transactions in block, processing and sending to RabbitMQ
        :param block: processing slot number
        :param pub_keys: set of public keys of our wallets. We are looking for transactions from this list
        """
        # Get block with number from params
        response_block = await self.__session.post(f'https://{SOLANA_URL}', json={
            "jsonrpc": "2.0", "id": 1, "method": "getBlock",
            "params": [block, {'encoding': 'jsonParsed', "transactionDetails": "full", "rewards": True}]
        })
        # Checking response
        if not response_block.ok:
            return False
        # Get result of response, if it's exists
        block_json = await response_block.json()
        if 'result' not in block_json.keys():
            return False
        block = block_json['result']
        # Processing list of transactions (around 2.000 records for block)
        transactions = []
        for transaction in block['transactions']:
            result = await self.__process_transaction(transaction, pub_keys, block_time=block['blockTime'])
            if result is None:
                continue
            transactions.append(result)
        # If there is some transactions, then sending to RabbitMQ
        if len(transactions) == 0:
            return True
        # Sending message to RabbitMQ
        return await self.__rabbit_mq.send_message([
            {"network": 'solana', "block": block},
            {"transactions": transactions}
        ])

    # Method for web application's endpoint. Search old transactions for user from request
    async def get_history_by_public_key(self, request: web.Request):
        """
        request params: {
            :pub_key: Account public key.
            :before: (optional) Start searching backwards from this transaction signature.
                    If not provided the search starts from the top of the highest max confirmed block.
                    1000 - default. [1-1000]
            :until: (optional) Search until this transaction signature, if found before limit reached.
            :limit: (optional) Maximum transaction signatures to return (between 1 and 1,000, default: 1,000).
        }
        """
        async with AsyncClient(f"https://{SOLANA_URL}") as client:
            params = {
                'limit': request.rel_url.query.get('limit'),
                'before': request.rel_url.query.get('before'),
                'until': request.rel_url.query.get('until')
            }
            pub_key = request.rel_url.query.get('pub_key')
            if params.get('limit') is not None:
                params['limit'] = int(params.get('limit', 10))

            # Get all transaction's signatures for user by public key
            response = await client.get_signatures_for_address(
                account=PublicKey(pub_key),
                **{x: y for x, y in params.items() if y is not None}
            )
            # Processing and sending transactions to RabbitMQ
            for record in response['result']:
                asyncio.create_task(
                    self.process_and_send_transaction_by_sig(sig=record['signature'], pub_keys={pub_key})
                )
        return web.Response(body='{status: "start"}')

    # Method for processing RPCResponse from json to our format for RabbitMQ
    async def __process_transaction(self, json: dict, pub_keys: Set[str], block_time: Optional[int] = None):
        meta = json['meta']
        # Get some fields for more comfortable access
        fee = meta['fee']
        message = json['transaction']['message']
        account_keys = message["accountKeys"]

        # Senders and recipients for transaction
        senders = []
        recipients = []

        # Here we checking all instructions and saving useful information about it
        total_amount = 0
        for preBalance, postBalance, account in zip(
            meta['preBalances'], meta['postBalances'], account_keys
        ):
            if account['pubkey'] in pub_keys:
                amount = postBalance - preBalance
                if amount == 0:
                    continue
                data = {'pubkey': account['pubkey'], 'amount': abs(amount),}
                if amount > 0:
                    recipients.append(data)
                elif amount < 0:
                    senders.append(data)
                total_amount += amount
        # If we can't find senders or recipients in our wallets, then this transaction unuseful for us. Just skip
        if len(senders) == 0 or len(recipients) == 0:
            return None

        time = block_time if block_time is not None else json['result']['blockTime']

        # It's view of transaction for RabbitMQ
        return {
            'time': time,
            'date': await time_str_from_timestamp(time),
            'transactionHash': json['result']['transaction']['signatures'],
            'amount': total_amount,
            'fee': fee,
            'slot': json['slot'],
            'recentBlockhash': message['recentBlockhash'],
            'senders': senders,
            'recipients': recipients
        }

    async def process_and_send_transaction_by_sig(self, sig: str, pub_keys: Set[str]):
        # Getting transaction by signature
        try:
            transaction = await self.__session.post(
                url=f'https://{SOLANA_URL}',
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    'params': [sig, 'jsonParsed']
                }
            )
        except:
            return
        # We can't get transaction. Solana or our node is died :D
        if not transaction.ok:
            return
        json = await transaction.json()
        # Transaction don't exist
        if json.get('result') is None:
            return
        # Transaction finished without errors
        if 'Ok' not in json['result']['meta']['status'].keys():
            return
        transaction_response = await self.__process_transaction(json['result'], pub_keys)
        if transaction_response is None:
            return
        # Aggregate json in typical for our system view
        message_for_rabbit = [
            {"network": 'solana', "block": json['result']['slot']},
            {'address': transaction_response['senders'][0], "transactions": [transaction_response]}
        ]
        # Sending message to RabbitMQ
        await self.__rabbit_mq.send_message(message_for_rabbit)

    async def __init(self):
        is_start_rabbit = await self.__rabbit_mq.connect()
        is_start_db = await self.__db.start()
        if not (is_start_db and is_start_rabbit):
            logger.error('START WAS CANCELLED')
            return False

        # Init aiohttp client
        if self.__session is None:
            jar = CookieJar(unsafe=True, quote_cookie=False)
            self.__session = ClientSession(cookie_jar=jar)
        return True


async def test_web_service(*_):
    return web.Response(body="{'status': 'OK'}")


demon = TransactionDemon()

app.add_routes([web.get('/check-old-transactions', demon.get_history_by_public_key)])
app.add_routes([web.get('/', test_web_service)])
