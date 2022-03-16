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
Run script via console

> Run the script from number to number.
>```shell
> python search_in_history_script.py -s startBlockNumber -e endBlockNumber
> python search_in_history_script.py --start startBlockNumber --end endBlockNumber

> Run the script for the block list 
> ```shell
> python search_in_history_script.py -b 'blockNumber blockNumber blockNumber ...'
> python search_in_history_script.py --blocks 'blockNumber blockNumber blockNumber ...'

> Run the script (ONLY WITH '-b --blocks' OR '-s --start -e --end') with the wallet address or addresses
> ```shell
> python search_in_history_script.py -b 'blockNumber blockNumber blockNumber ...' -a 'walletAddress walletAddress'
> python search_in_history_script.py -s startBlockNumber ...' --addresses 'walletAddress walletAddress'


> Also allowed.
> ```shell
> python search_in_history_script.py -s startBlockNumber
> python search_in_history_script.py --start startBlockNumber
> 
> python search_in_history_script.py -e endBlockNumber
> python search_in_history_script.py --end endBlockNumber
>
> python search_in_history_script.py -b 'blockNumber'
> python search_in_history_script.py --block 'blockNumber'
> 
> python search_in_history_script.py -e startBlockNumber -a 'walletAddress'
> python search_in_history_script.py -end startBlockNumber --addresses 'walletAddress'

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

### Format for Tron Network

```json

[
  {
    "network": "tron",
    "block": 36370775
  },
  {
    // The TRX transaction
    "address": "TYyrx59zDyUCwH4XHgPBdXtZzserMfQDxh",
    "transactions": [
      {
        "time": 1639646604000,
        "date": "16-12-2021 12:23:24",
        "transactionHash": "7adf0ab1f388eaad973e2db54c97b963fee0b96a46ebb898a993151963093763",
        "fee": 0,
        "senders": [
          {
            "address": "TYyrx59zDyUCwH4XHgPBdXtZzserMfQDxh",
            "amount": "0.000009"
          }
        ],
        "recipients": [
          {
            "address": "TEcE7tL39CFE2aebpN2L4iyAiGEaGFXS3h",
            "amount": "0.000009"
          }
        ],
        "amount": "0.000009"
      }
    ]
  }
]
```

### Format for Tron TRC20 USDT Network

```json
[
  {
    "network": "tron_trc20_usdt",
    "block": 36947360
  },
  {
    "address": "TAzsQ9Gx8eqFNFSKbeXrbi45CuVPHzA8wr",
    "transactions": [
      {
        "time": 1641377280000,
        "datetime": "05-01-2022 13:08:00",
        "transactionHash": "621adc64a6b4ba6bde18a1774104bdb6449d01397c9f26f5e44fbc7c5557da9e",
        "fee": "4.44168",
        "senders": [
          {
            "address": "TAzsQ9Gx8eqFNFSKbeXrbi45CuVPHzA8wr",
            "amount": "13.3320800"
          }
        ],
        "recipients": [
          {
            "address": "TUtmoBEdG5X6oJvU46M1CPokiZAUgANJnP",
            "amount": "13.3320800"
          }
        ],
        "amount": "13.3320800",
        "token": "TetherToken (USDT)"
      }
    ]
  }
]
```

### Format for Tron TRC20 USDC Network

```json
[
  {
    "network": "tron_trc20_usdc",
    "block": 37007557
  },
  {
    "address": "TYE218dMfzo2TH348AbKyHD2G8PjGo7ESS",
    "transactions": [
      {
        "time": 1641377280000,
        "datetime": "07-01-2022 15:20:06",
        "transactionHash": "ca9d28d7f7ea901e6a80c48a669f7dea94f6ddf2676a286282b89bd63b561099",
        "fee": "4.05948",
        "senders": [
          {
            "address": "TYE218dMfzo2TH348AbKyHD2G8PjGo7ESS",
            "amount": "2300"
          }
        ],
        "recipients": [
          {
            "address": "TVe6CEVVS69agsSXnjXzEABrWhY3mzn3j1",
            "amount": "2300"
          }
        ],
        "amount": "2300",
        "token": "FiatTokenProxy (USDC)"
      }
    ]
  }
]
```