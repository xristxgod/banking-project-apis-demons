from ..node import btc
from typing import List, Optional
from config import decimal, Decimal, logger


def get_fee_for_transaction(inputs: int, outputs: int, size: int) -> (Decimal, Decimal):
    """
    :param inputs: number of senders.
    :param outputs: number of receivers.
    :param size: size of transaction.
    :return: Tuple(transactions' fee, max fee rate in BTC/KB)
    """
    fees = btc.get_optimal_fees(from_=inputs, to_=outputs)
    return (
        decimal.create_decimal(fees['BTC/BYTE']) * decimal.create_decimal(size) * 4,
        decimal.create_decimal(fees['BTC/KB']) * 4
    )


def get_admin_fee_without_blockchain_fee(admin_fee, admin_wallet, fee):
    if admin_fee is not None and admin_wallet is not None:
        if admin_fee - fee > 0:
            return admin_fee - decimal.create_decimal(fee)
    return decimal.create_decimal(0)


def create_transaction(
        from_address: str, outputs: List[dict], private_key: str,
        admin_wallet: Optional[str] = None,
        admin_fee: Optional[Decimal] = None
):
    transactions_from: List[dict] = btc.get_transactions_for_address(private_key=private_key)
    inputs = []
    input_amount = decimal.create_decimal(0)
    amount: Decimal = sum([sum([decimal.create_decimal(value) for value in x.values()]) for x in outputs])

    with_admin = (admin_fee is not None and admin_wallet is not None)

    if with_admin:
        if not isinstance(admin_fee, Decimal):
            admin_fee = decimal.create_decimal(admin_fee)
        outputs.insert(0, {admin_wallet: "%.8f" % admin_fee})
        logger.error(f'AMOUNTS: {admin_fee} | {amount}')

    transactions_from = list(sorted(
        transactions_from,
        key=lambda x: sum([
            decimal.create_decimal(r['amount']) for r in x['recipients']
            if r['address'] == from_address
        ]),
        reverse=True
    ))

    for transaction in transactions_from:
        logger.error(f'TX: {transaction}')
        recipients = transaction['recipients']
        for recipient in recipients:
            if recipient['address'] == from_address:
                break
        else:
            continue
        if not btc.rpc_host.is_trx_unspent(transaction['transactionHash'], recipient['n']):
            continue
        input_amount += decimal.create_decimal(recipient['amount'])
        inputs.append({
            'txid': transaction['transactionHash'],
            'vout': recipient['n']
        })

        check_tx, _ = btc.create_unsigned_transaction(
            inputs=inputs, outputs=outputs,
        )
        fee, fee_rate = get_fee_for_transaction(len(inputs), len(outputs), check_tx['size'])

        admin_fee_without_blockchain_fee = get_admin_fee_without_blockchain_fee(admin_fee, admin_wallet, fee)

        logger.error(f'AMOUNT ALL: {input_amount} | {amount} | {fee} | {admin_fee_without_blockchain_fee}')
        if input_amount >= amount + fee + admin_fee_without_blockchain_fee:
            cashback = input_amount - amount - fee - admin_fee_without_blockchain_fee
            if cashback == 0:
                break
            fee, fee_rate = get_fee_for_transaction(len(inputs), len(outputs) + 1, check_tx['size'])

            admin_fee_without_blockchain_fee = get_admin_fee_without_blockchain_fee(admin_fee, admin_wallet, fee)

            cashback = input_amount - amount - fee - admin_fee_without_blockchain_fee

            if input_amount != amount + fee + admin_fee_without_blockchain_fee + cashback:
                continue
            else:
                outputs.append({
                    from_address: '%.8f' % cashback
                })
                if with_admin:
                    outputs[0] = {admin_wallet: '%.8f' % admin_fee_without_blockchain_fee}
                break
    else:
        logger.error(f'OUT: {outputs}')
        return {'error': 'Not enough btc'}
    unsigned_tx, _ = btc.create_unsigned_transaction(
        inputs=inputs, outputs=outputs,
    )
    return {
        **unsigned_tx,
        'fee': '%.8f' % fee,
        'maxFeeRate': '%.8f' % fee_rate
    }
