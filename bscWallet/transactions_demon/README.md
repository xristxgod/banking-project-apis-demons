ETHEREUM API for Python
===================

Search for ETH positions in a transaction array of addresses.

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


Search for transactions in the transferred range of blocks. From and to
--------------
>In the above case, you must pass the start and end of the search to the input.
You can also transfer an array of addresses if you do not need addresses in the database.
`start` must be less than `end`.
`end` should not exceed the height of the `blocks`.
Required arguments: `start: int`, `end: int`.


```-s 1234``` or ```--start 1234``` - left block number in range

```-e 4444``` or ```--end 4444``` - last block number in range

```-a address_1,address_2``` or ```--addresses address_1,address_2``` - addresses for search

### But you can use next special word:

```-a all``` or ```--addresses all``` - you can get all addresses from database


```shell

python search_in_history_script.py -s startBlockNumber
python search_in_history_script.py --start startBlockNumber

python search_in_history_script.py -e endBlockNumber
python search_in_history_script.py --end endBlockNumber
 
python search_in_history_script.py -e startBlockNumber -a walletAddress
python search_in_history_script.py -end startBlockNumber --addresses walletAddress
```

Json response
----------
>Json response which will be sent to RabbitMQ. Looks like that:

    # If everything was specified correctly
    [
      {
        "network": "eth",
        "block":13665124
      },
      {
        "address": "0xdfd5293d8e347dfe59e90efd55b2956a1343963d",
        "transactions": [
          {
            "time": 1636983793,
            "datetime": "15-11-2021 16:43:13"
            "transactionHash": "87f4cf14d03bf669b760e2365403bce55cb2841ac6435bd040e63d4f6476ba11",
            "amountETH": "0.11065423 ",
            "fee": "0.00380100",
            # Input 
            "senders": ["0xdfd5293d8e347dfe59e90efd55b2956a1343963d"],
            # Output
            "recipients": ["0x937391d6addfa17d0ebdec91156fd06ccd0e0f50"]
          }, 
          ...
        ]
      },
    ...
    ]
