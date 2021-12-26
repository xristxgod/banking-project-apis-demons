Demon for monitoring transactions in Solana network
===================================================

----------------------------------

For running demon you should start `run_demon.py` script.

Here we import a transaction finder and web application for making 
extra actions with Solana API and finding old transactions for our wallets.

``` python
from demon import demon, web, app, loop


if __name__ == '__main__':
    loop.create_task(demon.start_demon_parser_of_network())
    web.run_app(app, loop=loop)
```

-------------------------------------

For script work should use async connections to DB and RabbitMQ.
You can find this in `database.py` and `rabbit_mq.py`.

Class `DB` from `database.py` has only one method for getting users' addresses and wallets from our DB.

Class `RabbitMQ` from `rabbit_mq.py` provides access to RabbitMQ Queue and sends messages to the channel.
We use this for saving transactions' information for the next processing.

---------------------------------------

Web application interface
=========================

This is work on aiohttp web server.

There is 2 endpoints:
> Send to RabbitMQ old transactions for user's public key | `GET` | /check-old-transactions
> 
> Health check | `GET` | /

----------------------------------------

Format of JSON for RabbitMQ
===========================

``` json

[
    {
        "network": "solana",
        "block": 12342
    },
    {
        "transactions": [
            {
                "time": 1637592793,
                "date": "22-11-2021 17:57:13",
                "transactionHash": "49Mxe1Wcy18Bvug66C6LGr3kn4WWEhEvVdDtTcvvdjxyjE7TyupVEwiLwVEd5MCfnCp41VqQ1YFwXw3ykFRcPAAK",
                "amount": 141352,
                "fee": 5000,
                "slot": 1245,
                "recentBlockhash": ExV6eoxiz7vVYK82eZyaQyitC7qgRhYXz11xrDcfhtpe,
                "senders": [
                    {
                        "pubkey": "11111111111111111111111111111111",
                        "amount": 141352,
                    },
                    {
                        "pubkey": "11111111111111111111111111112345",
                        "amount": 4,
                    }
                ],
                "recipients": [
                    {
                        "pubkey": "22222222222222222222222222222222",
                        "amount": 141350,
                    },
                    {
                        "pubkey": "33333333333333333333333333333333",
                        "amount": 6,
                    }
                    ...
                ]
            }
        ]
    }
]

```


----------------------------------------

Main part of script. Demon.
===========================

For start, we created new event loop for our demon and web app.

``` python
# Init new event loop for async app
loop = asyncio.new_event_loop()

# Web application for adding new wallets in demon and checking transaction's history
app = web.Application()
```

All actions for searching new transactions in network exec by `class TransactionDemon`.
This class provides access to Solana RPC API. It's monitoring Solana's network and looking for transactions
for out wallets from DB.

``` python
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
```

------------------------

## Method for Demon startup

``` python
async def start_demon_parser_of_network(self):
    # Connecting to RabbitMQ and DB
    is_start_rabbit = await self.__rabbit_mq.connect()
    is_start_db = await self.__db.start()
    if not (is_start_db and is_start_rabbit):
        logger.error('START WAS CANCELLED')
        return

    # Init aiohttp client
    jar = CookieJar(unsafe=True, quote_cookie=False)
    self.__session = ClientSession(cookie_jar=jar)

    # Getting pub keys for our wallets
    pub_keys = await self.__db.get_pub_keys()

    # Split all keys for 100 groups and running this groups in different coroutines
    for index, pub_keys_groups in enumerate(
        await TransactionDemon.split_list(pub_keys, 100),
        TransactionDemon.FIRST_GROUP_ID
    ):
        # Start a coroutine
        asyncio.create_task(
            self.handler_transactions_for_group(index, pub_keys_groups),
        )
```

-----------------------------------------

## Method for getting current block height

Return current block height.

``` python
async def __get_current_block(self) -> Optional[int]
```

-----------------------------------------

## Method for getting transactions in block's range.

It's method for scrypt in `search_in_history_script.py`. Running with params
> param start: starting slot for searching transactions
>
> param end: last slot for searching transactions
> 
> param pub_keys: set of public keys of our wallets. We are looking for transactions from this list
> 
> return: bool. True, if all blocks from range was sending to RabbitMQ

``` python
async def get_transactions_in_blocks_range(
    self, 
    start: int,
     end: Optional[int] = None,
    *, 
    pub_keys: Optional[Set[str]] = None
):
```

-----------------------------------------

## Processing block and inner transactions. Sending block to RabbitMQ.

> Method for checking transactions in block, processing and sending to RabbitMQ 
> 
> param block: processing slot number
> 
> param pub_keys: set of public keys of our wallets. We are looking for transactions from this list
    

``` python
async def __check_block_and_send_to_rabbit_mq(
    self,
    block: int,
    pub_keys: Set[str]
)
```

-----------------------

## Method for processing transaction from RPC Response to our format

Return the dict for transaction from block, if there are mentions of one or more our public keys.

``` python
async def __process_transaction(
    self,
    json: dict,
    pub_keys: Set[str], 
    block_time: Optional[int] = None
)
```


------------------------

Web application.
================

### Endpoint for getting transactions' history by public key.

There is request with params.

Params structure:

```
request params: {
    :pub_key: Account public key.
    :before: (optional) Start searching backwards from this transaction signature.
            If not provided the search starts from the top of the highest max confirmed block.
            1000 - default. [1-1000]
    :until: (optional) Search until this transaction signature, if found before limit reached.
    :limit: (optional) Maximum transaction signatures to return (between 1 and 1,000, default: 1,000).
}
```

``` python
async def get_history_by_public_key(self, request: web.Request)
```