ETHEREUM API for Python
===================
A Python API for interacting with the ETHEREUM (ETH)


Usage
------
### Specify the API endpoints:

### All documentation:
> Documentation: | `GET`:`http://127.0.0.1:5000/documentation` 

### Wallet:
> Create ethereum wallet: | `POST`:`http://127.0.0.1:5000/create-wallet`

> Create deterministic ethereum wallet: | `POST`:`http://127.0.0.1:5000/create-deterministic-wallet`

> Push ethereum balance: | `GET`:`http://127.0.0.1:5000/get-balance`

### Token:
> Push token balance: | `GET`: `http://127.0.0.1:5000/get-token-balance`

> Add a new token: | `GET`: `http://127.0.0.1:5000/add-new-token` 

> Get all tokens: | `GET`: `http://127.0.0.1:5000/get-all-tokens` 

### Transaction ETH:
> Create and sign transaction: | `POST`:`http://127.0.0.1:5000/create-transaction` 

> Send the transaction: | `POST`:`http://127.0.0.1:5000/sign-send-transaction`

### Transaction Token:
> Create and sign a token transaction: | `POST`:`http://127.0.0.1:5000/create-token-transaction` 

> Send the token transaction: | `POST`:`http://127.0.0.1:5000/send-token-transaction` 

### Rest:
> Receive complete transaction: | `GET`: `http://127.0.0.1:5000/get-transaction` 

> Get optimal gas: | `GET`: `http://127.0.0.1:5000/get-optimal-gas` 

> Get gas price: | `GET`: `http://127.0.0.1:5000/get-gas-price`

-------

# Create a ETH wallet using the API
> Arguments:
>> `words : str` - it is a list of words that store all the information specific to recovering an ethereum wallet. (Optional)

    import requests
    url = "http://127.0.0.1:5000/create-wallet"
    
    # First way: without "mnemonic phrase"
    walletOne = requests.post(url).json()
    
    # Second way: with "mnemonic phrase"
    words = "execute damp badge rival thumb avoid balance plastic problem extend project silent"
    walletTwo = requests.post(url, json={"words": words}).json()

#### Response body:
    {
      "mnemonicWords": "execute damp badge rival thumb avoid balance plastic problem extend project silent",
      "privateKey": "0x355a7cbdc0caecd1e419809a9acd47d7bb5356d59acfa21c7bdde9f291fe9ba8",
      "publicKey": "026dfee067f62808c252d288bc47a7266765cc5dde03e38f437e19b4d19092dbe8",
      "address": "0x97c510A4E80F1023791115c46b9CcA73f4410F3E"
    }

--------

# Create Hierarchical Deterministic Wallet
> Arguments:
>> `words : str` - it is a list of words that store all the information specific to recovering an ethereum wallet. (Optional)
>
>> `child : int` - Number of addresses to be created. (Optional)

    import requests
    url = "http://127.0.0.1:5000/create-deterministic-wallet"
    
    # First way: without "mnemonic phrase"
    walletOne = requests.post(url).json()
    
    # Second way: with "mnemonic phrase" and with "child"
    words = "execute damp badge rival thumb avoid balance plastic problem extend project silent"
    child = 2
    walletTwo = requests.post(url, json={"words": words, "child": child}).json()

#### Response body:
    {
      "mnemonicWords": "evoke liquid feature naive innocent reunion into excuse move forget ordinary plastic",
      "privateKey": "0x42cf049e5948d99783342541df1a02688168fb7f1c777e990d439f802d0106f3",
      "publicKey": "02059f9ee7c28cbec0ccd9410d6f3a2a7aca61754090b7d81abb32b1814b2f839f",
      "addresses": {
                       "m/44'/60'/0'/0/1": {
                                              "address": "0x3b791961322d6584dEd3914B98B780AC07be10E3",
                                              "privateKey": "0x39fa7b0eab380bc6d548003992ae0f750adec351577517b652cc91c7d8946003",
                                              "publicKey": "03b436fe5b6ab48be2c4476bfa4b9235b1857a2858a6be3607cb2fd08fd1d5bd81"
                                            }
                       "m/44'/60'/0'/0/2": {
                                              "address": "0x55F90700BB07d912FAb68F8b56b8aeB7a42C8C27",
                                              "privateKey": "0xde5a9e186e588fef0088da64edea184d1cf483371fa83bc7e91ae967a3c1a646",
                                              "publicKey": "03573bfba5a01ccd3db1999d77e538fc11a0b4ee01165f7ceb8353dcedcebc66e7"
                                            },
                    }
    }
-------

# Get Ethereum balance
> Arguments:
>> `address : str` - Wallet address for which you need to get balance. (Required)

    import requests
    url = "http://127.0.0.1:5000/get-balance"

    address = "0x991E6F3b740d65548FA8a24e36B3e2a7c191839a"
    balance = requests.get(url, json={"address": address}).json()

#### Response body:

    {
      "balance": "87.99916" # The balance is specified in ethereum
    }

---------

# Create and sign a transaction right away
> Arguments:
>> `privateKey : str` - Private key of the sponsor for signing the transaction. (Required)
>
>> `fromAddress : str` - Sender's address (Required)
>
>> `toAddress : str` - Recipient address (Required)
>
>> `amount : int or float` - The amount to be sent should be indicated in ethereum (Required)
>
>> `gas: int` - This is the maximum amount of gas that is willing to pay to confirm a transaction (Optional). Default 100000

    import requests
    url = "http://127.0.0.1:5000/transaction/create-transaction"

    from_address = "0xEdcE8ECFCa8068baA7b7E5544aF1378A8d0C2375"
    from_private_key = "430abc622f0f7143d375a6a8de285cf5fc6118c21267d37d157f6a2936511be9"
    to_address = "0xa3A77708cb95a4820DD754A21B04AfC6eEf7Df35"
    amount = 2.23
    gas = 200000
    transaction = requests.post(url, 
        json={
            "fromAddress": from_address,
            "privateKey": from_private_key,
            "toAddress": to_address,
            "amount": amount,
            "gas": gas
        }).json()

#### Response body:

    {
      "rawTransaction": "0xf86d018504a817c80083030d4094a3a77708cb95a4820dd754a21b04afc6eef7df35881ef28d2f591f0000801ca015747913b67473f1206250587083a9ee79662c94e515de59c1d6367bdf527c04a01ecbf63239b01027d6669c304e0d10b8856529235b5e5b6b4ed31cc6005a0e6b" 
    }

---------

# Send signed transaction
> Arguments:
>> `createTxHex : str` - hash of the transaction that was previously signed `but not sent`. (Required)

    import requests
    url = "http://127.0.0.1:5000/sign-send-transaction"
    
    trx_hash = "0xf86d018504a817c80083030d4094a3a77708cb95a4820dd754a21b04afc6eef7df35881ef28d2f591f0000801ca015747913b67473f1206250587083a9ee79662c94e515de59c1d6367bdf527c04a01ecbf63239b01027d6669c304e0d10b8856529235b5e5b6b4ed31cc6005a0e6b"
    transaction_hash = requests.post(url, json={"createTxHex": trx_hash}).json()

#### Response body:
    {
      "transactionHash": "0x5e2c1b9926eae77c32bd0d59886fc66d13e61b03a90ac5218f646443057f9be5"
    }
---------

# Get transaction
> Arguments:
>> `trxHash : str` - Transaction hash `only already sent`. (Required)

    import requests
    url = "http://127.0.0.1:5000/get-transaction"
    
    trx_hash = "0x5e2c1b9926eae77c32bd0d59886fc66d13e61b03a90ac5218f646443057f9be5"
    transaction = requests.get(url, json={"trxHash": trx_hash}).json()

#### Response body:
    {
      "blockNumber": 2,
      "blockHash": "0xef8d73fe0981e0634dc31ab46aec3a9b135ce66949757e78e1c82c72b671e9ca",
      "transactionHash": "0x5e2c1b9926eae77c32bd0d59886fc66d13e61b03a90ac5218f646443057f9be5",
      "from": "0xEdcE8ECFCa8068baA7b7E5544aF1378A8d0C2375",
      "to": "0xa3A77708cb95a4820DD754A21B04AfC6eEf7Df35",
      "amount": "2.23",
      "gas": 200000,
      "gasPrice": 20000000000,
    }

--------

# Get optimal fee
> Arguments:
>> `fromAddress` - Sender's address (Required)
> 
>> `toAddress` - Recipient address (Required)
>
>> `amount` - The amount to be sent should be indicated in ethereum (Required)

    import requests
    url = "http://127.0.0.1:5000/get-optimal-gas"
    
    from_address = "0xEdcE8ECFCa8068baA7b7E5544aF1378A8d0C2375"
    to_address = "0xa3A77708cb95a4820DD754A21B04AfC6eEf7Df35"
    amount = 2.23
    gas = requests.get(url, 
        json={
            "fromAddress": from_address,
            "toAddress": to_address,
            "amount": amount,
        }).json()

#### Response body:
    {
      "gas": 21000,
    }

--------

Token (smart-contract)
=====

# Get all tokens

    import requests
    url = "http://127.0.0.1:5000/get-all-tokens"
    
    tokens = requests.get(url).json()

#### Response body:

    [
      # The list may be replenished
      "BNB", "USDT", "USDC", ... 
    ]

--------

# Add new token 
> Arguments:
>> `address : str` - Smart counter(token) address (Required)
> 
>> `token : str` - Token name (Optional)

    import requests
    url = "http://127.0.0.1:5000/add-new-token"
    
    address = "0xa47c8bf37f92abed4a126bda807a7b7498661acd"
    transaction_hash = requests.post(url, json={"address": address}).json()

#### Response body:
    {
      "message": "The token 'UST' has been added"
    }
---------

# Get token balance
> Arguments:
>> `address : str` - Token owner address (Required)
> 
>> `token : str` - Token name (Required)

    import requests
    url = "http://127.0.0.1:5000/add-new-token"
    
    address = "0xEdcE8ECFCa8068baA7b7E5544aF1378A8d0C2375"
    token = "BNB"
    transaction_hash = requests.post(url, json={"address": address, "token": token}).json()

#### Response body:
    {
      "balance": "13.1233" # Balance in token
      "token": "BNB", 
      "balanceETH": "13.1233" # Balance in ethereum
    }
---------

# Create, sign and send a token transaction right away
> Arguments:
>> `privateKey : str` - Private key of the sponsor for signing the transaction. (Required)
>
>> `fromAddress : str` - Sender's address (Required)
>
>> `toAddress : str` - Recipient address (Required)
>
>> `amount : int or float` - The amount to be sent should be indicated in ethereum (Required)
> 
>> `token : str` - Token name (Required)
>
>> `gas: int` - This is the maximum amount of gas that is willing to pay to confirm a transaction (Optional). Default 100000

    import requests
    url = "http://127.0.0.1:5000/send-token-transaction"
    
    from_address = "0x10bd8C0dF37736009F827bf105E36487104AA5e3"
    from_private_key = "ef5e4333fafb9b14763f6489ebab063ae6ff2b04595e1d97c7c5141e91d40e5a",
    to_address = "0xC398780c28Ed3F62C0F7B93AFc5c8AA6914cD1A7"
    amount = 2.03
    token = "Bnb"
    gas = 40000
    transaction_hash = requests.post(url, 
        json={
            "fromAddress": from_address,
            "privateKey": from_private_key,
            "toAddress": to_address,
            "amount": amount,
            "token": token,
            "gas": gas
        }).json()

#### Response body:
    {
      "transactionHash": "0xc67884f4c8e72c9555c6e3c08f05cad3e7c0a59763b6f525dbc48b84d5b8115c"
    }

# Send the token transaction
> Arguments:
>> `privateKey : str` - Private key of the sponsor for signing the transaction. (Required)
>
>> `fromAddress : str` - Sender's address (Required)
>
>> `toAddress : str` - Recipient address (Required)
>
>> `amount : int or float` - The amount to be sent should be indicated in ethereum (Required)
> 
>> `token : str` - Token name (Required)
>
>> `gas: int` - This is the maximum amount of gas that is willing to pay to confirm a transaction (Optional). Default 100000

    import requests
    url = "http://127.0.0.1:5000/token/sign-token-transaction"
    
    from_address = "0x10bd8C0dF37736009F827bf105E36487104AA5e3"
    from_private_key = "ef5e4333fafb9b14763f6489ebab063ae6ff2b04595e1d97c7c5141e91d40e5a",
    to_address = "0xC398780c28Ed3F62C0F7B93AFc5c8AA6914cD1A7"
    amount = 2.03
    token = "Bnb"
    gas = 40000
    transaction_hash = requests.post(url, 
        json={
            "fromAddress": from_address,
            "privateKey": from_private_key,
            "toAddress": to_address,
            "amount": amount,
            "token": token,
            "gas": gas
        }).json()

#### Response body:
    {
      "createTxHex": "0xf86d018504a817c80083030d4094a3a77708cb95a4820dd754a21b04afc6eef7df35881ef28d2f591f0000801ca015747913b67473f1206250587083a9ee79662c94e515de59c1d6367bdf527c04a01ecbf63239b01027d6669c304e0d10b8856529235b5e5b6b4ed31cc6005a0e6b"
    }
