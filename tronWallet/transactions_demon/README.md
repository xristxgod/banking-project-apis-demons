TRON API for Python
===================

Search for Tron positions in a transaction array of addresses.

Usage
=====

Before starting in the `.env` file:

>1. Specify `RabbitMQURL`, this is the path to RabbitMQ via `amqp` or `amqps` protocol. It is necessary to send the verified addresses to the queue.
    >`Example: "amqp://guest:guest@localhost:5672/%2F", "amqp://www-data:rabbit_pwd@rabbit1/web_messages"`
>2. Specify the `Queue` name of the queue to which the already verified data will be sent.
>3. Specify the `DataBaseURL` path to the database, you need to take the address from the database. `Example: "postgresql://postgres:mamedov00@localhost/acc"`
>4. Specify the `TronGridAPIKEY` or `listTronGridAPIKEY` api key or keys for TronGird to connect to the node. You can get it on the website: `https://www.trongrid.io/`
>5. Specify the `MultiKeys` set `True` if `listTronGridAPIKEY` is used.
>6. Specify the `NETWORK` enter one of the provided networks: `Mainnet`, `ShastaTestnet`, `NileTestnet`

------------
File `config.py`:
>1. `ERROR` - A file that will be created by itself when an error occurs, errors will be written to it. Default: error.txt
>2. `PILLOW` - Created automatically, records the last block that was checked but not sent to the queue. Default: rescue_pillow.json

Search for transactions by node.
--------------
Run script through IDE.

```python

from transactions_demon.src.demon import TransactionDemon
from asyncio import run

if __name__ == '__main__':
    # Run script for permanent work
    run(TransactionDemon().start())
    # Run the script from number to number
    start = 36552329 
    end = 36552335
    run(TransactionDemon.start(
        start_block=start, 
        end_block=end
    ))
```   
Run script via console

>Run the script from number to number.
>```shell
> python search_in_history_script.py -s startBlockNumber -e endBlockNumber
> python search_in_history_script.py --start startBlockNumber --end endBlockNumber


>Also allowed.
> ```shell
> python search_in_history_script.py -s startBlockNumber
> python search_in_history_script.py --start startBlockNumber
> 
> python search_in_history_script.py -e endBlockNumber
> python search_in_history_script.py --end endBlockNumber


------------------

```shell
>>> Demon is starting
>>> Write last block to: C:\...\transactions_demon\files\last_block.txt
>>> Run new iteration: start = 1640249047.580398
>>> Start processing transactions
>>> End processing transactions
>>> Write to C:\...\transactions_demon\files\last_block.txt new number: 36552330
>>> Getting started: 2021-12-23 11:44:08 | Block: 36552330
>>> New TX in Block: 36552330
>>> End block: 36552330. Time taken: 0:00:00 sec
```

Format of JSON for RabbitMQ
----------


``` json

[
    {
        "network": "tron",
        "block": 36370775
    },
    {   
        // The token TRC10 transaction
        "address": "TQbxcxnxSdYdV14f5XCe2ggeYi8bhPs7qW",
        "transactions": [
            {
                "time": 1639646604000,
                "date": "16-12-2021 12:23:24",
                "transactionHash": "1f83cf1fa055aecb7f81ed2b4f1916f54befa6de740cd6370bb9ee7dea5dec0a",
                "transactionType": "TransferAssetContract",
                "fee": 0,
                "senders": "TQbxcxnxSdYdV14f5XCe2ggeYi8bhPs7qW",
                "recipients": "TB8E4uPDd4fdjq8eoBfUsZZ4JCrbMM1KxL", 
                "amount": "1.888888", 
                "token": "AAANFT (AAANFT)"               
            }
        ]
    }, 
    {   
        // The token TRC20 transaction
        "address": "TKHypLsX2dEJ8NxtyKDxuQk5Sm25kiucvB",
        "transactions": [
            {
                "time": 1639646604000,
                "date": "16-12-2021 12:23:24",
                "transactionHash": "00ee9a020d26091e23c3ebf38631992dff20e1a75e3e47105bf4bb12942f764f",
                "transactionType": "TriggerSmartContract",
                "fee": "4.46968",
                "senders": "TKHypLsX2dEJ8NxtyKDxuQk5Sm25kiucvB",
                "recipients": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t", // Smart Contract (Token) address
                "smartContract": {
                    "toAddress": "TX5qYBwAM8EKGHLYqtjVNJmgbqqfUu5y6P", 
                    "amount": "740.27", 
                    "token": "Tether USD (USDT)"
                }               
            }
        ]
    }, 
    {   
        // The TRX transaction
        "address": "TYyrx59zDyUCwH4XHgPBdXtZzserMfQDxh",
        "transactions": [
            {
                "time": 1639646604000,
                "date": "16-12-2021 12:23:24",
                "transactionHash": "7adf0ab1f388eaad973e2db54c97b963fee0b96a46ebb898a993151963093763",
                "transactionType": "TransferContract",
                "fee": 0,
                "senders": "TYyrx59zDyUCwH4XHgPBdXtZzserMfQDxh",
                "recipients": "TEcE7tL39CFE2aebpN2L4iyAiGEaGFXS3h", 
                "amount": "	0.000009"             
            }
        ]
    },
    {
        // The Vote transaction 
        "address": "TM1zzNDZD2DPASbKcgdVoTYhfmYgtfwx9R",
        "transactions": [
            {
                "time": 1639646604000,
                "date": "16-12-2021 12:23:24",
                "transactionHash": "43d5296737904230be0d920a558ccb1fcda3dda447aaa374eb0643c6cafd81b2",
                "transactionType": "VoteWitnessContract",
                "fee": 0, 
                "senders": "TM1zzNDZD2DPASbKcgdVoTYhfmYgtfwx9R", 
                "voteAddress": "TJvaAeFb8Lykt9RQcVyyTFN2iDvGMuyD4M", 
                "voteCount": 170000000
            }
        ]
    }, 
    {
        // The freeze balance transaction
        "address": "TQT8oMviyRPrgAiD7WTU7ftnAdqQxVQV3a", 
        "transactions": [
            {
                "time": 1639646604000,
                "date": "16-12-2021 12:23:24",
                "transactionHash": "5fd2299adad50532cc1521704129b7db8345bf3ce453def279b924962b584bea",
                "transactionType": "FreezeBalanceContract",
                "fee": 0, 
                "senders": "THf2UtjK2KrQ6SoqUYr4DQrMCPpxRZbgLY", // The address that provides resources for freezing.
                "recipients": "TQT8oMviyRPrgAiD7WTU7ftnAdqQxVQV3a", // The user who receives `ENERGY` or` BANDWIDTH`. This may not always be the case, because senders can only freeze the balance for themselves.
                "resource": "ENERGY", // Resources that the user receives for freezing. `ENERGY` or` BANDWIDTH`
                "amount": "1.0" // Frozen TRX
            }
        ]
    }, 
    {
        // The unfreeze balance transaction
        "address": "TTwYVfg5Qt2RoWFJybnvJMyod2ULUUGggx", 
        "transactions": [
            {
                "time": 1639646604000,
                "date": "16-12-2021 12:23:24",
                "transactionHash": "194dcecc3f304c787e7bd758701bb88ace70a8184449034b042abd625f560dbb",
                "transactionType": "UnfreezeBalanceContract",
                "fee": 0, 
                "senders": "TTwYVfg5Qt2RoWFJybnvJMyod2ULUUGggx", // The user who unfreezes the balance
                "recipients": "TQT8oMviyRPrgAiD7WTU7ftnAdqQxVQV3a", // User whose account is being unfrozen
                "resource": "ENERGY", // What gets for defrosting. `ENERGY` or` BANDWIDTH`
            }
        ]
    }
]

```