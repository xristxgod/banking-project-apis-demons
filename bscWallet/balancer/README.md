# "Balancer" for BSC wallets

### Is small service for sending all native coins and tokens to main wallet


`init_sending_to_main_wallet.py` - demon for sending native coins and tokens
after receiving them to one of our wallet.

`receive_from_main_wallet.py` - demon for sending tokens after receiving them 
from one of our wallet, if on previous step was not enough native coins for paying for a gas.


### You can initialize sending to main wallet from scrypt `send_all_script.py`

You should enter to docker container and run next command:

``` bash
python send_all_script.py --address "address_of_wallet" --token "USDT" --limit "0.02"
```

> `--address` - from this address will send an amount equal to the balance in one transaction.
> If you don't use this parameter script will send money from all wallets to main wallet

> `--token` - will send only balances in this token. You can use `bsc` here, for sending 
> native coins - BNB. If you don't use this parameter script will send all tokens on wallet
 
> `--limit` - if you use this parameter, then script will send money only if there is more 
> then this value. In default limit is equal to `fee * DUST_MULTIPLICATOR`.
> DUST_MULTIPLICATOR - is value from `.env` file