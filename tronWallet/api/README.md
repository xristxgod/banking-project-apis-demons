TRON API for Python
===================

A Python API for interacting with the Tron

Usage
------
### Specify the API endpoints:


### Documentation:
------------
> Documentation on the page:  | `GET`:`http://127.0.0.1:8000/docs` or `GET`: `http://127.0.0.1:8000/redoc` |

> Documentation in json: | `GET`:`http://127.0.0.1:8000/docs-json` |

### Wallet:
> Create Tron wallet: | `POST`:`http://127.0.0.1:5000/create-wallet` |

> Get TRX balance: | `GET`:`http://127.0.0.1:5000/get-balance/{address}` |

### Token info:
> Get all tokens: | `GET`:`http://127.0.0.1:5000/get-all-tokens` |

### Account info:
> Get resource info of an account: | `GET`:`http://127.0.0.1:5000/get-account-resource/{address}` |

> Get the remaining bandwidth on your account: | `GET`:`http://127.0.0.1:5000/get-unspent-bandwidth/{address}` |

> Get the remaining energy on your account: | `GET`:`http://127.0.0.1:5000/get-unspent-energy/{address}` |

### Token TRC10:
> Get TRC10 balance: | `GET`:`http://127.0.0.1:5000/get-trc10-balance/{address}/{token}` |

### Token TRC20:
> Get TRC20 balance: | `GET`:`http://127.0.0.1:5000/get-trc20-balance/{address}/{token}` |

> Add new TRC20 token: | `GET`:`http://127.0.0.1:5000/add-trc20-token` |

### Fee info
> Find out what will be the commission for TRX and TRC10 transactions: | `GET`:`http://127.0.0.1:5000/get-fee/{address}` |

> Receive a fixed transaction fee for the TRC20 token: | `GET`:`http://127.0.0.1:5000/get-trc20-fee/{token}` |

### Transaction:
> Get transaction by transaction hash: | `GET`:`http://127.0.0.1:5000/get-transaction/{trxHash}` |

> Get all transactions by address: | `GET`:`http://127.0.0.1:5000/get-all-transactions/{address}` |

> Get the number of all received TRX: | `GET`:`http://127.0.0.1:5000/get-received/{address}` |

> Get the number of all TRX send: | `GET`:`http://127.0.0.1:5000/get-send/{address}` |

> Get all the commission spent on transactions: | `GET`:`http://127.0.0.1:5000/get-fee-spent/{address}` |

### Transaction TRX:
> Create a TRX transaction: | `POST`:`http://127.0.0.1:5000/create-transaction` |

### Transaction token TRC10:
> Create a TRC10 transaction: | `POST`:`http://127.0.0.1:5000/create-trc10-transaction` |

### Transaction token TRC20:
> Create a TRC20 transaction: | `POST`:`http://127.0.0.1:5000/create-trc20-transaction` |

### Freeze and Unfreeze:
> Create a transaction to freeze the balance for 3 days: | `POST`:`http://127.0.0.1:5000/create-freeze-balance` |

> Create a transaction to unfreeze the balance after 3 days of freezing: | `POST`:`http://127.0.0.1:5000/create-unfreeze-balance` |

### Transfer:
> Sign and send the created transaction: | `POST`:`http://127.0.0.1:5000/sign-send-transaction` |

----------------

# Create a Tron wallet using the API:
IMPORTANT!!! This account will become active after adding at least 0.1 TRX to his account!!!
> Arguments:
>> `passphrase : str` - Secret word for account recovery. (Optional)

```python
import requests
url = 'http://127.0.0.1:5000/create-wallet'

# First way: without `passphrase`
walletOne = requests.request("POST", url, json={}).text

# Second way: with `passphrase`
passphrase = "71rj8JBsk82pX6Grywm3"
walletTwo = requests.request("POST", url, json={"passphrase": passphrase}).text

print(walletTwo)
```

```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/create-wallet' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "passphrase": "71rj8JBsk82pX6Grywm3"
}'
```


#### Response body:

```json
{
  "passphrase": "71rj8JBsk82pX6Grywm3",
  "privateKey": "289e31762c5785706a62e92c034fd2caad3f0bb17b68bbf56a503049fb33656c",
  "publicKey": "244645126e56912ca394ca41d01475efa5daaeea0269704289ffee16dd33875345855b4bcade379567a5b2c027ae5d8c56f43c1f6bee5dc30bf571501ce38dfd",
  "address": "TQfwCQEHwqcdKQACtWDNeRzGmDxh5cnPiA",
  "message": "IMPORTANT!!! This account will become active after adding at least 0.1 TRX to his account!!!"
}
```
------------------

# Add a new TRC20 token
> Arguments:
>> `address : str` - Address of the smart contract (token). (Required)

```python
import requests
url = "http://127.0.0.1:8000/add-trc20-token"

contractAddress = "TKfjV9RNKJJCqPvBtK8L7Knykh7DNWvnYt"

status = requests.request("POST", url, json={"address": contractAddress})
print(status)
```

```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/add-trc20-token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "address": "TKfjV9RNKJJCqPvBtK8L7Knykh7DNWvnYt"
}'
```

#### Response body:

```json
{
  "message": "The token 'WBTT' is already in the system"
}
```

# Create TRX transaction:
> Arguments:
>> `fromAddress : str` - Sender's address (Required) \
>> `toAddress : str` - Recipient address (Required) \
>> `amount : int or float` - The amount to be sent should be indicated in TRX (Required)

```python
import requests
url = "http://127.0.0.1:5000/create-transaction"

txn = {
    "fromAddress": "TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb",
    "toAddress": "TA4D7YnFJiYCyHzrrgBLUmRoizUGtHJfRV",
    "amount": 1.1
}
create_transaction = requests.post(url, json=txn).text
print(create_transaction)
```   

```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/create-transaction' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "fromAddress": "TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb",
  "toAddress": "TA4D7YnFJiYCyHzrrgBLUmRoizUGtHJfRV",
  "amount": "1.1",
}'
```

#### Response body:

```json
{
  "createTxHex": "7b22636f6e7472616374223a...534633035363761227d",
  "bodyTransaction": {
    "txID": "7a9660626b5924b4da06d834314f673ec8c2c7c9d65720b0d2de62e4def5cdb8",
    "raw_data": {
      "contract": [
        {
          "parameter": {
            "value": {
              "owner_address": "4160818e26d83b148763fa258a4f537d18ff0efa07",
              "to_address": "4100f22c579d4932a67461917ad14a9dbe4488763c",
              "amount": 1100000
            },
            "type_url": "type.googleapis.com/protocol.TransferContract"
          },
          "type": "TransferContract"
        }],
      "timestamp": 1640006861104,
      "expiration": 1640006921104,
      "ref_block_bytes": "ce13",
      "ref_block_hash": "b6e8a71a54c0567a"
    },
    "signature": []
  },
  "message": "You have about 2-5 minutes to sign and send the order. Otherwise, it will be deleted!!!"
}
```

# Create TRC10 transaction:
> Arguments:
>> `fromAddress : str` - Sender's address (Required) \
>> `toAddress : str` - Recipient address (Required) \
>> `amount : int or float` - The amount to be sent should be indicated in TRX (Required) \
>> `token : int or str` - Token ID or Name or Symbol. (Required)

```python
import requests
url = "http://127.0.0.1:5000/create-transaction/trc10"

txn = {
    "from_address": "TND3X7YUTFFaqgChrQMkUBL1dXPUG51mXk",
    "to_address": "TGj75oAXCnPkiYUiJvs7zSzG83KwWFdBjN",
    "amount": 1.1,
    "token": "Seed" # or Seed or 1000242
}
create_transaction = requests.post(url, json=txn).text
print(create_transaction)
```

```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/create-transaction' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "fromAddress": "TND3X7YUTFFaqgChrQMkUBL1dXPUG51mXk",
  "toAddress": "TGj75oAXCnPkiYUiJvs7zSzG83KwWFdBjN",
  "amount": "1.1",
  "token": 1000242
}'
```

#### Response body:

```json
{
  "createTxHex": "7b22636f6e7472616374223a205b7b22...35633734366335393966227d",
  "bodyTransaction": {
    "txID": "ac7dc56fff94f9641dbb9e9ecda1eeb0635a83cbbcdd99c21f94046403d72313",
    "raw_data": {
      "contract": [
        {
          "parameter": {
            "value": {
              "owner_address": "4160818e26d83b148763fa258a4f537d18ff0efa07",
              "to_address": "4100f22c579d4932a67461917ad14a9dbe4488763c",
              "amount": 1100000,
              "asset_name": "31303030323432"
            },
            "type_url": "type.googleapis.com/protocol.TransferAssetContract"
          },
          "type": "TransferAssetContract"
        }],
      "timestamp": 1640007199119,
      "expiration": 1640007259119,
      "ref_block_bytes": "ce84",
      "ref_block_hash": "df67da5c746c599f"
    },
    "signature": []
  },
  "message": "You have about 2-5 minutes to sign and send the order. Otherwise, it will be deleted!!!"
}
```

# Create TRC20 transaction:
> Arguments:
>> `fromAddress : str` - Sender's address (Required) \
>> `toAddress : str` - Recipient address (Required) \
>> `amount : int or float` - The amount to be sent should be indicated in TRX (Required) \
>> `token : str` - Token Symbol or Name or SmartContract (Token) address. (Required) \

```python
import requests
url = "http://127.0.0.1:5000/create-transaction/trc10"

txn = {
    "fromAddress": "TBA6CypYJizwA9XdC7Ubgc5F1bxrQ7SqPt",
    "toAddress": "TFuz4pf1An9uj25nruWnhizamLratdDX2u",
    "amount": 50,
    "token": "USDT"
}
create_transaction = requests.post(url, json=txn).text
print(create_transaction)
```

```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/create-transaction' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "fromAddress": "TBA6CypYJizwA9XdC7Ubgc5F1bxrQ7SqPt",
  "toAddress": "TFuz4pf1An9uj25nruWnhizamLratdDX2u",
  "amount": "50",
  "token": "USDT"
}'
```

#### Response body:

```json
{
  "createTxHex": "7b22636f6e747261asfasf23a205b7b22...356337343fa393966227d",
  "bodyTransaction": {
    "txID": "943553d3518136d7e89b4941e12eec7dbfe5e6c314c818f1f6ba68321d93a21e",
    "raw_data": {
      "contract": [
        {
          "parameter": {
            "value": {
              "data": "a9059cbb0000000000000000000000414134b5897913880dba8d261fbc44ad86b49f993b0000000000000000000000000000000000000000000000000000000002faf080",
              "owner_address": "41a614f803b6fd780986a42c78ec9c7f77e6ded13c",
              "contract_address": "410d0707963952f2fba59dd06f2b425ace40b492fe"
            },
            "type_url": "type.googleapis.com/protocol.TriggerSmartContract"
          },
          "type": "TriggerSmartContract"
        }],
      "expiration": 1639490650004,
      "ref_block_bytes": "075e",
      "ref_block_hash": "be1a8dfe8818d06f",
      "fee_limit": 10000000 // 10000000 SUN = 10 TRX - this is fee for transaction
    },
    "signature": []
  },
  "message": "You have about 2-5 minutes to sign and send the order. Otherwise, it will be deleted!!!"
}
```

# Create freeze balance
> Arguments:
>> `ownerAddress : str` - The address of the owner on which to block the balance (Required) \
>> `amount : int or float` - The number of TRX that need to be blocked (Required) \
>> `resource : str` - Block TRX to get: ENERGY or BANDWIDTH. Default=ENERGY (Optional)

```python
import requests
url = "http://127.0.0.1:5000/create-freeze-balance"

freeze = {
    "ownerAddress": "TA4D7YnFJiYCyHzrrgBLUmRoizUGtHJfRV",
    "amount": 1.1,
    "resource": "ENERGY"
}
create_freeze = requests.get(url, json=freeze)
print(create_freeze)
```

```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/create-freeze-balance' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "ownerAddress": "TA4D7YnFJiYCyHzrrgBLUmRoizUGtHJfRV",
  "amount": "1.1",
  "resource": "ENERGY"
}'
```

#### Response body:

```json
{
  "createTxHex": "7b22636f6e747261637425b7b22...261623265393539227d",
  "bodyTransaction": {
    "txID": "4329791caa51a00497281ed5dcc2171e24db8b1edeaa936a79f562b2d50333b6",
    "raw_data": {
      "contract": [
        {
          "parameter": {
            "value": {
              "owner_address": "4100f22c579d4932a67461917ad14a9dbe4488763c",
              "frozen_balance": 1100000,
              "frozen_duration": 3,
              "resource": "ENERGY"
            },
            "type_url": "type.googleapis.com/protocol.FreezeBalanceContract"
          },
          "type": "FreezeBalanceContract"
        }],
      "timestamp": 1640094646860,
      "expiration": 1640094706860,
      "ref_block_bytes": "4047",
      "ref_block_hash": "841028252ab2e959"
    },
    "signature": []
  },
  "message": "You have about 2-5 minutes to sign and send the order. Otherwise, it will be deleted!!!"
}
```

# Create unfreeze balance
> Arguments:
>> `ownerAddress : str` - The address of the wallet where you need to unlock the balance. (Required) \
>> `resource : str` - Unlock: ENERGY or BANDWIDTH. Default=ENERGY (Optional)

```python
import requests
url = "http://127.0.0.1:5000/create-freeze-balance"

freeze = {
    "ownerAddress": "TA4D7YnFJiYCyHzrrgBLUmRoizUGtHJfRV",
    "resource": "ENERGY"
}
create_freeze = requests.get(url, json=freeze)
print(create_freeze)
```

```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/create-unfreeze-balance' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "ownerAddress": "TA4D7YnFJiYCyHzrrgBLUmRoizUGtHJfRV",
  "resource": "ENERGY"
}'
```

#### Response body:

```json
{
  "createTxHex": "7b22636f6e747261637617261...1663831363261227d",
  "bodyTransaction": {
    "txID": "09a020cfa80745b0957d3d2455634f9cd1e40ad11fbec7441df5088efc7f0e9b",
    "raw_data": {
      "contract": [
        {
          "parameter": {
            "value": {
              "owner_address": "4100f22c579d4932a67461917ad14a9dbe4488763c",
              "resource": "ENERGY"
            },
            "type_url": "type.googleapis.com/protocol.UnfreezeBalanceContract"
          },
          "type": "UnfreezeBalanceContract"
        }],
      "timestamp": 1640094841673,
      "expiration": 1640094901673,
      "ref_block_bytes": "4088",
      "ref_block_hash": "361c9e6351f8162a"
    },
    "signature": []
  },
  "message": "You have about 2-5 minutes to sign and send the order. Otherwise, it will be deleted!!!"
}
```

# Sign and Send transaction:
> Arguments:
>> `privateKey : str` - Private key of the sponsor for signing the transaction. (Required) \
>> `createTxHex: str` - Encrypted raw data to send the transaction. (Required) \

```python
import requests
url = "http://127.0.0.1:5000/create-transaction"

# Sends 3 types of transactions: TRC20 (TriggerSmartContract), TRC10 (TransferAssetContract), TRX (TransferContract)
tnx = {
    "privateKey": "...",
    "createTxHex": "7b22636f6e7472616374223a...534633035363761227d"
}
send_transaction = requests.post(url, json=tnx)
print(send_transaction)
```
#### Response body:

```json
{
  "blockNumber": 36489258,
  "transactionHash": "19ac4e28a9f392182fa010fe2f8b50c869a499cfc90948e58694da26264f758d",
  "amount": "0.23",
  "fee": 0,
  "senders": ["TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb"],
  "recipients": ["TA4D7YnFJiYCyHzrrgBLUmRoizUGtHJfRV"]
}
```

#Transaction fee

-----
## TRX & TRC 10 transaction:
TRX and TRC10 transactions consume only `BANDWIDTH`. Every 24 hours, the bandwidth is replenished and equals 5000.
If you don't make a lot of transactions (one transaction is on average equal to 200-300 throughput, that is,
you can make about `17-18 transactions in 24 hours`), then you have nothing to worry about. And if there are more transactions,
then you can freeze a little TRX to get bandwidth. `1 TRX ≈ 1.63 bandwidth`. For a more accurate calculation,
you can refer to <a href="https://tronstation.io/calculator"> TRON STATION </a> a calculator for calculating both throughput and energy.
A certain amount of TRX is frozen for `72 hours or 3 full days`, after this time you can safely unfreeze and return
the funds back to the wallet without any losses. To pay a commission or not to pay is up to you to choose.
----
## TRC20 transaction:
The TRC20 transaction uses only `ENERGY` or TRX as a commission. Energy can only be obtained by freezing TRX. For example,
suppose the total number of TRX frozen for energy is 1,000,000,000 TRX in the current network, and one account freezes
1,000 TRX, which is one millionth of the total and is equal to 100,000 microseconds. If the contract execution takes
1000 microseconds, then the user can run the contract 100 times. When funds are frozen, it is impossible to get both
bandwidth points and Energy. If you freeze TRX to get bandwidth, then your energy will not change. `1 TRX ≈ 31.83 energy`.
For a more accurate calculation, you can refer to the <a href="https://tronstation.io/calculator"> TRON STATION </a>
calculator to calculate both throughput and energy.
---

# Get TRX balance:

```python
import requests

address = "TA4D7YnFJiYCyHzrrgBLUmRoizUGtHJfRV"
print(requests.request(
    "GET",
    f"http://127.0.0.1:5000/get-balance/{address}"
).text)
```

```shell
curl -X 'GET' \
  'http://127.0.0.1:8000/get-balance/TA4D7YnFJiYCyHzrrgBLUmRoizUGtHJfRV' \
  -H 'accept: application/json'
```

#### Response body:

```json
{
  "balance": "0.27",
  "token": "TRX"
}
```

# Account resource:
This method allows you to get account resources.

```python
import requests

address = "TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb"
print(requests.request(
    "GET",
    f"http://127.0.0.1:5000/get-account-resource/{address}"
).text)
```

```shell
curl -X 'GET' \
  'http://127.0.0.1:8000/get-account-resource/TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb' \
  -H 'accept: application/json'
```

#### Response body:
> `freeNetUsed` - Free bandwidth used \
> `freeNetLimit` - Total free bandwidth \
> `NetUsed` - Used amount of bandwidth obtained by staking \
> `NetLimit` - Total bandwidth obtained by staking \
> `TotalNetLimit` - Total bandwidth can be obtained by staking \
> `TotalNetWeight` - Total TRX staked for bandwidth \
> `tronPowerLimit` - TRON Power(vote) \
> `EnergyUsed` - Energy used \
> `EnergyLimit` - Total energy obtained by staking \
> `TotalEnergyLimit` - Total energy can be obtained by staking \
> `TotalEnergyWeight` - Total TRX staked for energy

# Get unspent bandwidth & energy

```python
import requests

address = "TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb"

print(requests.request(
    "GET",
    f"http://127.0.0.1:5000/get-unspent-bandwidth/{address}"
).text)

print(requests.request(
    "GET",
    f"http://127.0.0.1:5000/get-unspent-bandwidth/{address}"
).text)

```

```shell
curl -X 'GET' \
  'http://127.0.0.1:8000/get-unspent-bandwidth/TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb' \
  -H 'accept: application/json'
  
curl -X 'GET' \
  'http://127.0.0.1:8000/get-unspent-energy/TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb' \
  -H 'accept: application/json'  
```

#### Response body:

```json
[
  {
    "unspentBandwidth": 1500, // Remaining Bandwidth
    "bandwidthLimit": 1500,
    "bandwidthUsed": 0
  },
  {
    "unspentEnergy": 0, // Remaining energy
    "energyLimit": 0,
    "energyUsed": 0
  }
]
```

# Get received & send & fee spent

```python
import requests

address = "TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb"

print(requests.request(
    "GET",
    f"http://127.0.0.1:5000/get-received/{address}"
).text)

print(requests.request(
    "GET",
    f"http://127.0.0.1:5000/get-send/{address}"
).text)

print(requests.request(
    "GET",
    f"http://127.0.0.1:5000/get-fee-spent/{address}"
).text)
```

```shell
curl -X 'GET' \
  'http://127.0.0.1:8000/get-received/TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb' \
  -H 'accept: application/json'

curl -X 'GET' \
  'http://127.0.0.1:8000/get-send/TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb' \
  -H 'accept: application/json'

curl -X 'GET' \
  'http://127.0.0.1:8000/get-fee-spent/TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb' \
  -H 'accept: application/json'
```

#### Response body:

```json
[
  {
    "totalReceived": "10.48888800"
  },
  {
    "totalSend": "7.38888800"
  },
  {
    "totalFee": "2.20000000"
  }
]
```

# Get TRC10 balance

```python
import requests

address = "TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb"
token = 1004210     # AAANFT

print(requests.request(
    "GET",
    f"http://127.0.0.1:5000/get-trc10-balance/{address}/{token}"
).text)
```

```shell
curl -X 'GET' \
  'http://127.0.0.1:8000/get-trc10-balance/TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb/1004210' \
  -H 'accept: application/json'
```

#### Response body:

```json
{
  "balance": "2",
  "token": "AAANFT (AAANFT)"
}
```

# Get TRC20 balance

```python
import requests

address = "TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb"
token = "USDT"

print(requests.request(
    "GET",
    f"http://127.0.0.1:5000/get-trc20-balance/{address}/{token}"
).text)
```

```shell
curl -X 'GET' \
  'http://127.0.0.1:8000/get-trc20-balance/TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb/USDT' \
  -H 'accept: application/json'
```

#### Response body:

```json
{
  "balance": "15.3",
  "token": "TetherToken (USDT)"
}
```

# Get TRC10 fee 

```python
import requests

token = "USDT"

print(requests.request(
    "GET",
    f"http://127.0.0.1:5000/get-trc20-fee/{token}"
).text)
```

```shell
curl -X 'GET' \
  'http://127.0.0.1:8000/get-trc20-fee/USDT' \
  -H 'accept: application/json'
```

#### Response body:

```json
{
  "feeTRX": "10" // in TRX
}
```

# Get TRX and TRC10 fee

```python
import requests

fromAddress = "TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb"

print(requests.request(
    "GET",
    f"http://127.0.0.1:5000/get-fee/{fromAddress}"
).text)
```

```shell
curl -X 'GET' \
  'http://127.0.0.1:8000/get-fee/TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb' \
  -H 'accept: application/json'
```

#### Response body:

```json
{
  "feeTRX": "0" // in TRX
}
```

# Get transaction by tx hash 

```python
import requests

txHash = "2ce65ebb8e1d618826cee5fbb85050d05c8db82ae02ebba67486e448686ec019"

print(requests.request(
    "GET",
    f"http://127.0.0.1:5000/get-transaction/{txHash}"
).text)
```

```shell
curl -X 'GET' \
  'http://127.0.0.1:8000/get-transaction/2ce65ebb8e1d618826cee5fbb85050d05c8db82ae02ebba67486e448686ec019' \
  -H 'accept: application/json'
```

#### Response body:

```json
{
  "timestamp": 1640354736971,
  "datetime": "24-12-2021 17:05:36",
  "blockNumber": 36606678,
  "transactionHash": "2ce65ebb8e1d618826cee5fbb85050d05c8db82ae02ebba67486e448686ec019",
  "transactionType": "TriggerSmartContract",
  "fee": "0.35",
  "from": "TL8EGYuMebAVgHeXJ69bHKK9VxnHu7pmXH",
  "data": "a3082be900000000000000000000000000000000000000000000000000000000000000360000000000000000000000000000000000000000000000000000000000000001",
  "contractAddress": "TWmhXhXjgXTj87trBufmWFuXtQP8sCWZZV"
}
```

# Get all transactions by address

```python
import requests

address = "TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb"

print(requests.request(
    "GET",
    f"http://127.0.0.1:5000/get-all-transactions/{address}"
).text)
```

```shell
curl -X 'GET' \
  'http://127.0.0.1:8000/get-all-transactions/TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb' \
  -H 'accept: application/json'
```

#### Response body:

```json
[
  {
    "blockNumber": 36577352,
    "transactionHash": "59f04d1d984048cccc98c6d7ab1dc3ccd7bcbe326c51c69ba494a2697fa8541c",
    "fee": "0",
    "transactionType": "TransferAssetContract",
    "from": "TA4D7YnFJiYCyHzrrgBLUmRoizUGtHJfRV",
    "timestamp": 1640266720911,
    "datetime": "23-12-2021 16:38:40",
    "to": "TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb",
    "amount": "1",
    "token": "AAANFT (AAANFT)"
  },
    {
    "blockNumber": 36313683,
    "transactionHash": "e879168ea337331bc7d56894cde0974fd96cc6870711f1c6e9653026490a70a8",
    "fee": "1.1",
    "transactionType": "TransferContract",
    "from": "TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb",
    "timestamp": 1639473392825,
    "datetime": "14-12-2021 12:16:32",
    "to": "TA4D7YnFJiYCyHzrrgBLUmRoizUGtHJfRV",
    "amount": "1.1"
  },
  ...
]
```