SOLANA API for Python
===================

A Python API for interacting with the Solana

Usage
=====

Specify the API endpoints:

To install the testnet, change TestNet to True in the `.env` file

------------
> Create a wallet | `POST`:`http://127.0.0.1:5000/create-wallet/` |
> 
> Get a balance | `GET`:`http://127.0.0.1:5000/get-balance/` |
> 
> Create and send a transaction | `POST`:`http://127.0.0.1:5000/send-transaction/` |
------------

Create Solana wallet
====================
You can create a wallet using the secret word by POST request.

-------------
``` python
@app.route('/create-wallet', methods=['POST'])
@validate()
def route_create_wallet(body: BodyCreateWallet):
    return create_wallet(body=body)


def create_wallet(body: BodyCreateWallet) -> CreateWalletResponse:
    # We create a secret phrase for new wallet
    phrase, is_success = __create_secret_phrase()
    # If this isn't success just return error's text
    if not is_success:
        return {'error': phrase}
    # Else generating a public key for a new wallet
    public_key, is_success = __create_public_key(words=phrase, secret_word=body.secret_word)
    if not is_success:
        return {'error': public_key}
    # If creating a wallet was a success - return information about the new wallet
    return CreateWalletResponse(
        MnemonicPhrase=phrase,
        PublicKey=public_key,
        SecretWord=body.secret_word
    )
```

Body of request - is JSON with next structure:

``` python
class BodyCreateWallet(BaseModel):
    secret_word: str
```


Check wallet's balance by a public key
======================================
--------------------------------------
``` python
@app.route('/get-balance', methods=['GET'])
@validate()
def route_get_balance(query: QueryBalance):
    return get_balance(query=query)


def get_balance(query: QueryBalance):
    # Here we just use Solana API for getting balance for our user
    return solana_api.client.get_balance(
        pubkey=PublicKey(query.pubkey),
        commitment=query.commitment
    )
```

You can make request with next params:
``` python
class QueryBalance(BaseModel):
    pubkey: str
    commitment: Optional[Commitment] = None
```


Create transaction
==================

You can create and sign the new transactions with two public keys.

------------------


``` python
@app.route('/send-transaction', methods=['POST'])
@validate()
def route_send_transaction(body: BodySendTransaction):
    return send_transaction(body=body)


def send_transaction(body: BodySendTransaction):
    # Converting strings to PublicKey objects
    to_pubkey = PublicKey(body.to_pubkey)
    from_pubkey = PublicKey(body.from_pubkey)
    
    # Creating instructions for future transaction
    instruction = transfer(TransferParams(
        from_pubkey=from_pubkey,    # From
        to_pubkey=to_pubkey,        # To
        lamports=body.lamports      # How much of crypt we want to send
    ))
    # Send transaction and getting information about it
    transaction = __set_transaction(from_pubkey, instruction)
    # Get signature of new transaction
    signature = __sign_and_send_transaction(transaction)['result']
    # Return result of transaction's conformation 
    return solana_api.client.confirm_transaction(signature)
```

Body of request - is JSON with next structure:

``` python
class BodySendTransaction(BaseModel):
    from_pubkey: str        # From
    to_pubkey: str          # To
    lamports: int           # How much of crypt we want to send
```
