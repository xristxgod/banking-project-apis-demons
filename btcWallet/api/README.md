BITCOIN API for Python
===================

A Python API for interacting with the Bitcoin (BTC)

Usage
=====

Specify the API endpoints:

To install the testnet, change TestNet to True in the `.env` file

------------
>Create a wallet | `POST`:`http://api.btc.staging.mangobanking.com/create-wallet/` 

>Create Hierarchical Deterministic Wallet | `POST`:`http://api.btc.staging.mangobanking.com/create-deterministic-wallet/` 

>Get a balance | `GET`:`http://api.btc.staging.mangobanking.com/get-balance/` 

>Get all received bitcoins at address | `GET`:`http://api.btc.staging.mangobanking.com/get-received/` 

>Get all sent bitcoins at address | `GET`:`http://api.btc.staging.mangobanking.com/get-send/` 

>Create transaction with service's fee without sending | `POST`:`http://api.btc.staging.mangobanking.com/create-transaction-service`

>Create transaction without sending | `POST`:`http://api.btc.staging.mangobanking.com/create-transaction`

>Sign and send existing transaction | `POST`:`http://api.btc.staging.mangobanking.com/sign-send-transaction`

>Get all transactions | `GET`:`http://api.btc.staging.mangobanking.com/get-all-transactions/` 

>Get optimal fee | `GET`:`http://api.btc.staging.mangobanking.com/get-optimal-fee/` 

>Get unspent transactions| `GET`:`http://api.btc.staging.mangobanking.com/get-unspent/` 

Create a Bitcoin wallet using the API
--------------
You can create a wallet in 2 ways by specifying `"mnemonic phrase"`,
or provide an api to generate it for you.
------------
    import requests
    
    BASE = 'http://api.btc.staging.mangobanking.com/'

    def create(words=None):
        if words:
            response = requests.post(BASE + 'create-wallet', json={'words': words})
            return response.json()
        response = requests.post(BASE + 'create-wallet')
        return response.json()
-------

    # Method 1: By passing arguments "mnemonic phrase" consisting of 12 words.
    >>> phrase = 'seminar ensure voyage strike pass test regret follow below mango weekend useless'
    >>> create(words=phrase)
    >>> {
        "mnemonicWords": "seminar ensure voyage strike pass test regret follow below mango weekend useless",
        "privateKey": "KzdBkHzBpkG...",
        "publicKey": "0333a88c7b9e9...",
        "address": "1Kxj67HfT5MF5mCLyji7ahsDVGRWijHEtr"
    }   

    # Method 2: without specifying "mnemonic phrase"
    >>> create()
    >>> {
        "mnemonicWords": "ginger alone cross uniform position tip salt current corn forum kitten final",
        "privateKey": "L39tzpbPapEERop1xk...",
        "publicKey": "024ee9e174f94ac14a6abaf...",
        "address": "1E5YZmCGaotr6qG8A4kUDAgiHjLakytaN3",
    }

Create Hierarchical Deterministic Wallet
-----------
You can create a wallet in 2 ways by specifying `"mnemonic phrase"`,
or provide an api to generate it for you.
------------
    import requests
    
    BASE = 'http://api.btc.staging.mangobanking.com/'

    def create(words=None, child=None):
        if words:
            response = requests.post(BASE + 'create-deterministic-wallet', json={'words': words, "child": child})
            return response.json()
        response = requests.post(BASE + 'create-deterministic-wallet')
        return response.json()
-------

    # Method 1: By passing arguments "mnemonic phrase" consisting of 12 words.
    >>> phrase = 'seminar ensure voyage strike pass test regret follow below mango weekend useless'
    >>> child = 10 # Number of address
    >>> create(words=phrase, child=child)
    >>> {
        "mnemonicWords": "seminar ensure voyage strike pass test regret follow below mango weekend useless",
        "privateKey": "KzdBkHzBpkG...",
        "publicKey": "0333a88c7b9e9...",
        "addresses": {
            "m/44'/1'/0'/0/1": {"Address", "n1NU...", "PrivateKey": "cUEW...", "PublicKey": "03d1..."},
            ... # 10 more addresses
            "m/44'/1'/0'/0/10": {"Address", "mhFa...", "PrivateKey": "cRzy...", "PublicKey": "035c..."},
        }
    }   

    # Method 2: without specifying "mnemonic phrase"
    >>> create()
    >>> {
        "mnemonicWords": "ginger alone cross uniform position tip salt current corn forum kitten final",
        "privateKey": "L39tzpbPapEERop1xk...",
        "publicKey": "024ee9e174f94ac14a6abaf...",
        "addresses": {
            "m/44'/1'/0'/0/1": {"Address", "mppn...", "PrivateKey": "cUJL...", "PublicKey": "029c..."},
            ... # 10 more addresses
            "m/44'/1'/0'/0/10": {"Address", "mtmx...", "PrivateKey": "cU7P...", "PublicKey": "03b6..."},
        }
    }


Check the wallet balance at the privateKey
------------
------------
    
    import requests

    BASE = 'http://api.btc.staging.mangobanking.com/'
    
    def balance_at_address(privateKey):
        response = requests.get(BASE + 'get-balance', json={'privateKey': privateKey})
        return response.json()
------
    >>> privateKey = "1E5YZmCGao...jLakytaN3"
    >>> balance_at_address(privateKey=privateKey)
    >>> {
            "balance": "0.1241", # The balance is indicated in BTC.
    }

Get all received bitcoins at the address
------------
------------
    
    import requests

    BASE = 'http://api.btc.staging.mangobanking.com/'
    
    def get_received(private_key):
        response = requests.get(BASE + 'get-received', json={'address': address})
        return response.json()
------
    >>> address = "1E5YZmCGaotr6qG8A4kUDAgiHjLakytaN3"
    >>> get_received(address=address)
    >>> {
            "totalReceived": "1.0123", # The balance is indicated in BTC.
    }

Receive all sent bitcoins at the address
------------
    
    import requests

    BASE = 'http://api.btc.staging.mangobanking.com/'
    
    def get_send(private_key):
        response = requests.get(BASE + 'get-sent', json={'address': address})
        return response.json()
------
    >>> address = "1E5YZmCGaotr6qG8A4kUDAgiHjLakytaN3"
    >>> get_sent(address=address)
    >>> {
            "totalSent": "133.0123", # The balance is indicated in BTC.
    }


Create transaction with `adminFee` and `adminAddress`
----------

> `adminFee` - Comission for service. Really adminFee is equal to this value - fee of blockchain.

> `adminAddress` - Address for receiving service's comission (`adminFee`).

> `fromAddress` - The address of sender.  

> `privateKeys` - The private keys of senders.

> `outputs` - The outputs (key-value pairs), where none of the keys are duplicated.\
> {\
> "address": amount, # A key-value pair. The key (string) is the bitcoin address, the value (float or string) is the amount in BTC\
> ...\
> }

> Example:
> ``` json
> {
>    "adminFee": 0.0001235,
>    "adminAddress": "12fs23NBx42Q2z4235w...",
>    "fromAddress": "14vL4KbyjoA1TGtTUmqCgQkF8mPphUxMnL",
>    "privateKey": "KyeX2w7gouG...6rLxgs",
>    "outputs": [
>        {
>            "13Ev1r5jdbUJ5FviEETAYbf1BA6ycs65Kx": 0.000017
>        }
>    ]
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
>        },     # Amount of btc
>        {
>            "n": 1,
>            "scriptPubKey": {
>                "addresses": [
>                    "14vL4KbyjoA1TGtTUmqCgQkF8mPphUxMnL"
>                ],
>                "asm": "OP_DUP OP_HASH160 2afe54de8c7f09979c9ecb06ea996d4825cd663b OP_EQUALVERIFY OP_CHECKSIG",
>                "hex": "76a9142afe54de8c7f09979c9ecb06ea996d4825cd663b88ac",
>                "reqSigs": 1,
>                "type": "pubkeyhash"
>            },
>            "value": "0.00054389"
>        }      # Cashback
>    ],
>    "vsize": 119,
>    "weight": 476
> }
> ```


Create transaction without sending
-----------
> `fromAddress` - The address of sender.  

> `privateKeys` - The private keys of senders.

> `outputs` - The outputs (key-value pairs), where none of the keys are duplicated.\
> {\
> "address": amount, # A key-value pair. The key (string) is the bitcoin address, the value (float or string) is the amount in BTC\
> ...\
> }

> Example:
> ``` json
> {
>    "fromAddress": "14vL4KbyjoA1TGtTUmqCgQkF8mPphUxMnL",
>    "privateKey": "KyeX2w7gouG...6rLxgs",
>    "outputs": [
>        {
>            "13Ev1r5jdbUJ5FviEETAYbf1BA6ycs65Kx": 0.000017
>        }
>    ]
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
>        },     # Amount of btc
>        {
>            "n": 1,
>            "scriptPubKey": {
>                "addresses": [
>                    "14vL4KbyjoA1TGtTUmqCgQkF8mPphUxMnL"
>                ],
>                "asm": "OP_DUP OP_HASH160 2afe54de8c7f09979c9ecb06ea996d4825cd663b OP_EQUALVERIFY OP_CHECKSIG",
>                "hex": "76a9142afe54de8c7f09979c9ecb06ea996d4825cd663b88ac",
>                "reqSigs": 1,
>                "type": "pubkeyhash"
>            },
>            "value": "0.00054389"
>        }      # Cashback
>    ],
>    "vsize": 119,
>    "weight": 476
> }
> ```


Sign and send existing transaction
------------
> `privateKeys` - The base58-encoded private keys for signing \
> ["privateKey", ...] # private key in base58-encoding\
 
> `maxFeeRate` - Reject transactions whose fee rate is higher than the specified value, expressed in BTC/kB. 

> `createTxHex` - Existing transactions' hash in hex. You can get it in /create-transaction

> Example:
> ``` json
> {
>    "createTxHex": "0200000001fd463d9800357ab76...ac00000000",
>    "privateKeys": [
>        "KyeX2w7gouGFqC...2VPMq6rLxgs"
>    ],
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
>           {"address": "1gx56we5sgvqz23r2356b...", "amount": "0.00001246", "n": 1},
>           {"address": "ghr542345745ys23x45b3...", "amount": "0.00128000", "n": 2},
>           ...
>    ],
> }

```


Get all transactions 
------------
------------
    
    import requests

    BASE = 'http://api.btc.staging.mangobanking.com/'
    
    def get_all(addresses: list):
        response = requests.get(BASE + '/get-all-transactions', json={'addresses': addresses})
        return response.json()
------
    >>> addresses = ["1PdbJLPnFTkGJZSGj15LY5AhZcndnBPoSH", ...]
    >>> get_all(addresses=addresses)
    >>> [
          {
            "address": "1PdbJLPnFTkGJZSGj15LY5AhZcndnBPoSH",
            "transactions": [
              {
                "time": 1637043040,
                "datetime": "2021-11-16 09:10:40",
                "transactions_hash": "589ed3285561d89f3b1072f69069cc8ce2fe3c6a8599b5ba4127d6a9a716c119",
                "fee": "0.00023755",
                "amount": "1.22975531",
                "sender": [
                  {
                    "address": "1E8gSDjFHxi1pwm97bgDgFV129oCvKCwfX",
                    "amount": "1.22975531"
                  }
                ],
                "received": [
                  {
                    "address": "1PdbJLPnFTkGJZSGj15LY5AhZcndnBPoSH",
                    "amount": "0.01355617"
                  },
                  {
                    "address": "1K6htKt2FcviPWGJVAKTPrdacVynWBak2y",
                    "amount": "1.16558852"
                  },
                  {
                    "address": "bc1q6q4hxyjh06t3g96vyvr3leztex8vj7ecpx6njs",
                    "amount": "0.00300000"
                  },
                  {
                    "address": "bc1qqgjj8rfm6vcmjlea7mc8ret57rzdx7nuqd2agd",
                    "amount": "0.04737307"
                  }
                ]
              }
            ]
          }
        ]

Get optimal fee
------------
------------
    
    import requests

    BASE = 'http://api.btc.staging.mangobanking.com/'
    
    def get_fee_for_transaction(**kwargs):
        response = requests.get(BASE + 'get-optimal-fee', json=kwargs)
        return response.json()
--------------------------------
    >>> kw = {
    ...     "input": 50, # Number of inputs
    ...     "output" 50, # Number of outputs
    ...     "toConfirmWithin": 2 # Confirmation target in blocks (1 - 1008)
    >>> }
    >>> get_fee_for_transaction(**kw)
    >>> { 
    ...    "transfer": "50 input -> 50 output | blocks 2",
    ...    "BTC/KB": "0.00006213",
    ...    "SAT/KB": "6213",
    ...    "SAT/BYTE": "6.213",
    ...    "bytes": "10760",
    ...    "satoshi": "66851",
    ...    "btc": "0.00066852",
    >>> }


Get unspent transactions
------------
------------
    
    import requests

    BASE = 'http://api.btc.staging.mangobanking.com/'
    
    def get_unspent(address):
        response = requests.get(BASE + 'get-unspent', json={"address": address})
        return response.json()
--------------------------------
    >>> address = "1PdbJLPnFTkGJZSGj15LY5AhZcndnBPoSH"
    >>> get_unspent(address)
    >>> [
    ... ["confirmations", "scriptPubKey", "txid", "vout"],
        ...
    >>> ]


Description of all arguments
----------------
> `words` - Mnemonic phrases. 12 of 24 words (Optional)

> `child` - Number of addresses for hierarchical deterministic wallet (Optional)

> `address` - Wallet address (Required)

> `privateKey` - A private key serialized to the Wallet Import Format. If the argument is not supplied, 
                 a new private key will be created. The WIF compression flag will be adhered to, 
                 but the version byte is disregarded. Compression will be used by all new keys. (Required)

> `output` - (list of tuple) – A sequence of outputs you wish to send in the form 
             (destination, amount, currency). The amount can be either an int, float, 
             or string as long as it is a valid input to decimal.Decimal. The currency must be supported. (Required)

> ` fee` - The number of satoshi per byte to pay to miners. By default Bit will poll 
           https://bitcoinfees.earn.com and use a fee that will allow your transaction 
           to be confirmed as soon as possible. (Optional)
 
> `publicKeys` -  A list or set of public keys encoded as hex or bytes assigned to the multi-signature contract.
                  If using a list, then the order of the public keys will be used in  the contract. 
                  If using a set, then Bit will order the public keys according to lexicographical order. (Required)

> `count` - The number of required signatures to spend from this multi-signature contract. (Required)


After creating a transaction, you can check it here:
----------
`<https://www.blockchain.com/btc/unconfirmed-transactions>`

-----------------------
####And most importantly:
When creating a wallet, save all the data, namely `"Private Key"` and `"Mnemonic phrase"`. 
<span style="color: red">Store in a protected place...</span>