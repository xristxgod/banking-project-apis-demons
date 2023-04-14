# "Balancer" for Tron wallets

### Is small service for sending all native coins and tokens to main wallet

`init_sending_to_main_wallet.py` - demon for sending native coins and tokens
after receiving them to one of our wallet.

### You can initialize sending to main wallet from scrypt `send_all_script.py`

You should enter to docker container and run next command:

``` bash
python send_all_script.py --address "address_of_wallet" --token "USDT"
```

> `--address` - from this address will send an amount equal to the balance in one transaction.
> If you don't use this parameter script will send money from all wallets to main wallet

> `--token` - will send only balances in this token. You can use `tron` or `trx` here, for sending 
> native coins - TRX. If you don't use this parameter script will send all tokens on wallet