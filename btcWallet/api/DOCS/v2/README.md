BITCOIN API for Python
===================

A Python API for interacting with the Bitcoin (BTC)

Usage
=====

Specify the API endpoints:

To install the testnet, change TestNet to True in the `.env` file

------------
>Create a wallet | `POST`:`http://api.btc.staging.mangobanking.com/v2/btc/create-wallet/` 

>Import existing wallet | `POST`:`http://api.btc.staging.mangobanking.com/v2/btc/import-wallet/` 

>Get a balance | `POST`:`http://api.btc.staging.mangobanking.com/v2/btc/get-balance/` 

>Create transaction without sending | `POST`:`http://api.btc.staging.mangobanking.com/v2/btc/create-transaction`

>Sign and send existing transaction | `POST`:`http://api.btc.staging.mangobanking.com/v2/btc/sign-send-transaction`


Create a Bitcoin wallet using the API
--------------
You can create a wallet in 2 ways by specifying `"mnemonic phrase"`,
or provide an api to generate it for you.
------------
    import requests
    
    BASE = 'http://api.btc.staging.mangobanking.com/v2/btc/'

    def create():
        response = requests.post(BASE + 'create-wallet')
        return response.json()
-------

    >>> create()
    >>> {
        "address": "188c31h...shaqYC3z",
        "path": "m/44'/0'/0'/0/0",
        "publicKey": "025b4a...43e20f63eb",
        "privateKey": "L5YZ1r...L4RNST7"
    }


Check the wallet balance at the address
------------
------------
    
    import requests

    BASE = 'http://api.btc.staging.mangobanking.com/v2/btc'
    
    def balance_at_address(privateKey):
        response = requests.get(BASE + 'get-balance', json={'address': address})
        return response.json()
------
    >>> privateKey = "188c31hPxLcZekAG9JXZX97mDtshaqYC3z"
    >>> balance_at_address(address=address)
    >>> {
        "balance": "0.1241", # The balance is indicated in BTC.
    }


Create transaction with `adminFee`
----------

### !!! First `VOUT` - is always adminFee for adminAddress. 
### If in request field `adminFee` is empty - then it will be equal to adminFee from .env

> `outputs` - The outputs (key-value pairs), where none of the keys are duplicated.
> 
> ``` json
> [
>   {
>       "address": amount, 
>       # A key-value pair. The key (string) is the bitcoin address, the value (float or string) is the amount in BTC
> 
>       "adminFee": "value"
>   },
>   {...},
> ]
>  ```

> Example:
> ``` json
> {
>    "outputs": [
>        {
>            "13Ev1r5jdbUJ5FviEETAYbf1BA6ycs65Kx": "0.000017"
>        }
>    ],
>    "adminFee": "0.002"
> }
> ```


> Result: 
> ``` json
> {
>    "createTxHex": "020000000...00000000",   # Hex of created transaction. Send it to /sign-send-transaction.
>    "fee": "0.00001785",                     # Fee for this transaction
>    "maxFeeRate": "0.00021063"               # Max fee rate for transaction in BTC/kB. Send it to /sign-send-transaction.
>    "hash": "539ca75a4e5baf8f914b450212e4e986832180ca3d7567a4538b0f4495aae700", # Transaction hash
>    "locktime": 0,
>    "size": 119,                                                                # Size of transaction in bytes
>    "txid": "539ca75a4e5baf8f914b450212e4e986832180ca3d7567a4538b0f4495aae700", # Transaction ID
>    "version": 2,
>    "vin": [
>        {
>            "scriptSig": {
>                "asm": "",
>                "hex": ""
>            },
>            "sequence": 4294967295,
>            "txid": "7727e7a0928252467a1f7ba1b543a16be3ac94c52027e008ef6a03dca5643ee5",
>            "vout": 1
>        }
>    ],     # Inputs for transaction
>    "vout": [
>        {
>            "n": 0,
>            "scriptPubKey": {
>                "addresses": [
>                    "13Ev1r5jdbUJ5FviEETAYbf1BA6ycs65Kx"
>                ],
>                "asm": "OP_DUP OP_HASH160 1891e9d60869223d99f38134418f7a6d3f6bf18e OP_EQUALVERIFY OP_CHECKSIG",
>                "hex": "76a9141891e9d60869223d99f38134418f7a6d3f6bf18e88ac",
>                "reqSigs": 1,
>                "type": "pubkeyhash"
>            },
>            "value": "0.00001700"
>        }     # Amount of btc
>    ],
>    "vsize": 119,
>    "weight": 476
> }
> ```


Sign and send existing transaction
------------ 

### !!! First `VOUT` - is always adminFee for adminAddress. 
### If in request field `adminFee` is empty - then it will be equal to adminFee from .env

> `adminFee` - Optional. Comission for service. Really adminFee is equal to this value - fee of blockchain.
 
> `maxFeeRate` - Reject transactions whose fee rate is higher than the specified value, expressed in BTC/kB. 

> `createTxHex` - Existing transactions' hash in hex. You can get it in /create-transaction

> Example:
> ``` json
> {
>    "createTxHex": "0200000001fd463d9800357ab76...ac00000000",
>    "adminFee": "0.0001235",
>    "maxFeeRate": "0.00005765"
> }
> ```

> Result: 
> ``` json
> {
>    "time": 12453463,
>    "datetime": "16-09-2021 15:12:57",
>    "transactionHash": "0200000001...1df235g",
>    "amount": "12.02101000",
>    "fee": "0.00005000",
>    "senders": [
>           {"address": "1gx56we5sgvqz23r2356b", "amount": "1.90001246"},
>           ...
>    ],
>    "recipients": [
>           {"address": adminFee},
>           {"address": "1gx56we5sgvqz23r2356b...", "amount": "0.00001246", "n": 1},
>           {"address": "ghr542345745ys23x45b3...", "amount": "0.00128000", "n": 2},
>           ...
>    ],
> }

```


After creating a transaction, you can check it here:
----------
`<https://www.blockchain.com/btc/unconfirmed-transactions>`

-----------------------
####And most importantly:
When creating a wallet, save all the data. 
Store in a protected place...