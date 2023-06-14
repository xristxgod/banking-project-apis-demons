import decimal

from tronpy.abi import trx_abi
from tronpy.exceptions import AddressNotFound
from tronpy.tron import PrivateKey, Transaction as TronTransaction

import trontxsize

from core.old_crypto.transaction.base import TransactionInterface, TransactionType
from core.old_crypto.transaction.base import TransactionBody, Commission


SMART_CONTRACT_TRANSACTION_TYPES = {
    'a9059cbb': ('transfer', '(address,uint256)', TransactionType.TRANSFER),
    '095ea7b3': ('approve', '(address,uint256)', TransactionType.APPROVE),
    '23b872dd': ('transferFrom', '(address,address,uint256)', TransactionType.TRANSFER_FROM),
}

TRANSACTION_TYPES = {
    'TransferContract': TransactionType.TRANSFER,
    'FreezeBalanceV2Contract': TransactionType.FREEZE,
    'DelegateResourceContract': TransactionType.FREEZE,
    'UnfreezeBalanceV2Contract': TransactionType.UNFREEZE,
    'UnDelegateResourceContract': TransactionType.UNFREEZE,
}


class Transaction(TransactionInterface):

    @classmethod
    def decoded_data(cls, data: str) -> tuple[tuple, TransactionType]:
        _, parameter, typ = SMART_CONTRACT_TRANSACTION_TYPES[data[:8]]
        return trx_abi.decode_single(parameter, data[8:]), typ

    def commission(self, payload: dict) -> Commission:
        raw_data = payload['raw_data']
        signature = payload['signature'] if payload['signature'] else '0' * 130

        if raw_data['contract'][0]['type'] == 'TransferContract':
            try:
                self.client.get_account(
                    raw_data['contract'][0]['parameter']['value']['to_address']
                )
            except AddressNotFound:
                return Commission(
                    amount=decimal.Decimal(1.1),
                    extra=dict(
                        bandwidth=100,
                        energy=0,
                    )
                )

        bandwidth = trontxsize.get_tx_size({
            'raw_data': raw_data,
            'signature': [signature or '0' * 130],
        })
        energy = 0
        if raw_data['contract'][0]['parameter']['value'].get('data'):
            data = raw_data['contract'][0]['parameter']['value']['data']
            name, parameter, _ = SMART_CONTRACT_TRANSACTION_TYPES[data[:8]]

            owner_address = raw_data['contract'][0]['parameter']['value']['owner_address']
            contract_address = raw_data['contract'][0]['parameter']['value']['contract_address']

            constant_contract = self.client.trigger_constant_contract(
                owner_address=owner_address,
                contract_address=contract_address,
                function_selector=name + parameter,
                parameter=data[8:],
            )
            energy = constant_contract['energy_used']

        amount = decimal.Decimal((energy * 1000) + (bandwidth * 400), context=decimal.Context(prec=999))
        if amount > 0:
            amount /= decimal.Decimal(1000000)

        return Commission(
            amount=amount,
            extra=dict(
                bandwidth=bandwidth,
                energy=energy,
            )
        )

    def make_response(self, transaction: dict) -> TransactionBody:
        parameter = transaction['raw_data']['contract'][0]['parameter']

        obj = TransactionBody
        typ = TRANSACTION_TYPES.get(parameter['type'])
        match typ:
            case TransactionType.TRANSFER:
                value = parameter['value']
                amount = from_sun(value['amount'])
                params = dict(
                    senders=[schemas.Participant(
                        address=value['owner_address'],
                        amount=amount,
                    )],
                    recipients=[schemas.Participant(
                        address=value['to_address'],
                        amount=amount,
                    )],
                    amount=amount,
                )
            case TransactionType.FREEZE | TransactionType.UNFREEZE:
                value = parameter['value']

                raw_amount = (
                        value.get('frozen_balance') or
                        value.get('unfreeze_balance') or
                        value.get('balance')
                )
                amount = from_sun(raw_amount)

                recipients = []
                if value.get('receiver_address'):
                    recipients.append(schemas.Participant(
                        address=value['receiver_address'],
                        amount=amount,
                    ))

                params = dict(
                    senders=[schemas.Participant(
                        address=value['owner_address'],
                        amount=amount,
                    )],
                    recipients=recipients,
                    amount=amount,
                )
            case _:
                # Smart contract transaction
                from core.node import node
                value = parameter['value']
                parameter, typ = cls.decode_data(parameter['data'])

                stable_coin = node.get_stable_coin(value['contract_address'])
                amount = stable_coin.to_decimal(parameter[-1])
                params = dict(
                    senders=[schemas.Participant(
                        address=value['owner_address'],
                        amount=amount,
                    )],
                    recipients=[],
                    amount=amount,
                    currency=stable_coin.symbol,
                )
                participant = schemas.Participant(
                    address=parameter[0],
                    amount=amount,
                )
                if len(parameter) == 2:
                    params['recipients'].append(participant)
                else:
                    params['senders'].append(participant)
                    params['recipients'].append(schemas.Participant(
                        address=parameter[1],
                        amount=amount,
                    ))

        commission = await cls.commission(raw_transaction['raw_data'], raw_transaction['signature'][0], client)

        return obj(
            timestamp=raw_transaction['timestamp'],
            commission=commission,
            type=typ,
            **params,
        )


    def sign(self, payload: dict, private_key: str) -> str:
        obj = TronTransaction.from_json(payload, client=self.client)
        signed_obj = obj.sign(
            priv_key=PrivateKey(
                private_key_bytes=bytes.fromhex(private_key),
            )
        )
        return signed_obj.to_json()

    def send(self, payload: dict) -> TransactionBody:
        obj = TronTransaction.from_json(payload, client=self.client)
        sent_obj = obj.broadcast()
        return self.make_response(sent_obj)
