BITCOIN API for Python | Transaction Search
===================

Search for BTC transactions in an array consisting of addresses.

------------

Run search transactions in range of blocks
==========================================

1. You should to join inside docker container:

> `docker exec -ti btc_demon bash`

2. Run one of the followings commands:

> `python search_in_history_script.py -s startBlockNumber -e endBlockNumber`
> 
> `python search_in_history_script.py -s startBlockNumber`
>
> `python search_in_history_script.py -e endBlockNumber`

`-s` is equal to `--start`

`-e` is equal to `--end`

-------------

Usage
=====

Before starting in the `.env` file:

>1. Specify `RabbitMQURL`, this is the path to RabbitMQ via `amqp` or `amqps` protocol. It is necessary to send the verified addresses to the queue.
>`Example: "amqp://guest:guest@localhost:5672/%2F", "amqp://www-data:rabbit_pwd@rabbit1/web_messages"`
>2. Specify the `Queue` name of the queue to which the already verified data will be sent.
>3. Specify the `DataBaseURL` path to the database, you need to take the address from the database. `Example: "postgresql://postgres:mamedov00@localhost/acc"`
>4. Create a file `last_block.txt `and make sure it's completely clean. The last block that was checked by the script will be written here. If there was some kind of error and the script suddenly turned off, the search will be carried out from the last block that was specified in the file, if you need to run completely from scratch, then just clean the file.
------------
File `findTransactionsBTCSettings.py`:
>1. `ERROR` - A file that will be created by itself when an error occurs, errors will be written to it. Default: error.txt
>2. `PILLOW` - Created automatically, records the last block that was checked but not sent to the queue. Default: rescue_pillow.json

Search for transactions by node.
--------------
After all the above actions have been performed, you can run the script.

```python
from src.demon import TransactionDemon

if __name__ == '__main__':
    TransactionDemon().start()
```   

------------------
    # If everything was specified correctly
    >>> Getting started: 2021-11-22 17:52:12 | Block: 710849
    >>> End block: 710849. Time taken: 0:00:12 sec
    >>> Getting started: 2021-11-22 17:52:12 | Block: 710850
    >>> End block: 710850. Time taken: 0:00:24 sec

Search for transactions in the transferred range of blocks. From and to
--------------
Json response
----------
>Json response which will be sent to RabbitMQ. Looks like that:

```json
    // If everything was specified correctly
    [
      {
        "network": "btc",
        "block": 710851
      },
      {
        "address": "1HxcQLAhRnyNHb7bLRWCVbPM2EAp3bg6Sn",
        "transactions": [
          {
            "time": 1637592793,
            "date": "22-11-2021 17:57:13"
            "transactionHash": "0a98fe9d7f44c6b06a987523664c0f7c68a7542894850719304bd009ddfcc17e",
            "amountBTC": "0.55576646 ",
            "fee": "0.00085276",
            # Input 
            "senders": [
              {
                "address": "1HxcQLAhRnyNHb7bLRWCVbPM2EAp3bg6Sn",
                "amountBTC": "0.55661922"
              }
            ],
            # Output
            "recipients": [
              {
                "address": "32eNxViyH9RH4j4eBwxqffUcvGhCjBNT1d",
                "amountBTC": "0.15270900"
              },
              {
                "address": "bc1q9fnchzqz9r4d4ptf7vyjy752aff7w4c86j5gpj",
                "amountBTC": "0.40305746"
              }
            ]
          }
          ...
        ]
      },
      ...
    ]
```