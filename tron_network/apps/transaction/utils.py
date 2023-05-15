import decimal

from tronpy.keys import to_base58check_address

from core.crypto import node
from core.crypto.utils import from_sun
from apps.transaction import schemas


def build_transaction(
        transaction: dict, transaction_type: schemas.TransactionType
) -> schemas.BaseResponseSendTransactionSchema:
    transaction_id = transaction['txID']
    transaction_info = await node.client.get_transaction_info(transaction_id)

    transaction_value = transaction_info['raw_data']['contract'][0]['parameter']['value']

    timestamp = transaction['raw_data']['timestamp']
    owner_address = transaction_value['owner_address']
    commission = schemas.ResponseCommission(
        fee=decimal.Decimal(transaction_info.get('fee', 0)),
        bandwidth=transaction_info.get('receipt', {}).get('net_usage', 0),
        energy=transaction_info.get('receipt', {}).get('energy_usage_total', 0),
    )

    match transaction_type:
        case schemas.TransactionType.TRANSFER_NATIVE:
            return schemas.ResponseSendTransfer(
                id=transaction_id,
                timestamp=timestamp,
                commission=commission,
                type=transaction_type,
                amount=from_sun(transaction_value['amount']),
                from_address=owner_address,
                to_addres=transaction_value['to_address'],
                currency='TRX',
            )
        case schemas.TransactionType.TRANSFER:
            data = transaction_value['data']
            contract = node.get_contract_by_contract_address(transaction_value['contract_address'])
            return schemas.ResponseSendTransfer(
                id=transaction_id,
                timestamp=timestamp,
                commission=commission,
                type=transaction_type,
                amount=contract.from_int(int(f'0x{data[72:]}', 0)),
                from_address=owner_address,
                to_addres=to_base58check_address(f'41{data[32:72]}'),
                currency=contract.symbol,
            )
        case schemas.TransactionType.APPROVE:
            # TODO
            pass
        case schemas.TransactionType.TRANSFER_FROM:
            # TODO
            pass
        case schemas.TransactionType.FREEZE:
            # TODO
            pass
        case schemas.TransactionType.UNFREEZE:
            # TODO
            pass
        case schemas.TransactionType.DELEGATE:
            # TODO
            pass
        case schemas.TransactionType.UN_DELEGATE:
            # TODO
            pass
