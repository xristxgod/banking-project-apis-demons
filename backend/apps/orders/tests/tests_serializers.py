import json

import pytest

from apps.orders.rest import serializers

from .factories import OrderFactory, DepositFactory


@pytest.mark.django_db
class TestDepositSerializer:
    def test_deposit_created(self):
        deposit = DepositFactory(is_created=True)

        data = serializers.DepositSerializer(deposit).data

        # Check structure & status created
        assert data == {
            'id': deposit.pk,
            'userId': deposit.order.user_id,
            'status': deposit.order.status,
            'verbose_status': deposit.order.get_status_display(),
            'chainId': deposit.order.currency.network.chain_id,
            'nodeUrl': deposit.order.currency.network.url,
            'blockExplorerUrl': deposit.order.currency.network.block_explorer_url,
            'paymentDetail': {
                'usdAmount': str(deposit.amount),
                'usdCommission': str(deposit.commission),
                'usdExchangeRate': str(deposit.usd_exchange_rate),
            },
            'orderDetail': {
                'amount': str(deposit.order.amount),
                'networkId': deposit.order.currency.network_id,
                'networkName': deposit.order.currency.network.name,
                'currencyId': deposit.order.currency_id,
                'currencySymbol': deposit.order.currency.symbol,
            },
            'transactionDetail': None,
            'can_send': True,
            'create': deposit.order.created,
            'update': deposit.order.updated,
        }

    def test_deposit_cancel(self):
        deposit = DepositFactory(is_cancel=True)

        data = serializers.DepositSerializer(deposit).data

        assert data['status'] == deposit.order.status
        assert data['verbose_status'] == deposit.order.get_status_display()
        assert data['can_send'] is False

    def test_deposit_done(self):
        deposit = DepositFactory(is_done=True)

        data = serializers.DepositSerializer(deposit).data

        assert data['status'] == deposit.order.status
        assert data['verbose_status'] == deposit.order.get_status_display()
        assert data['can_send'] is False

        assert data['transactionDetail'] == {
            'transactionHash': deposit.order.transaction.transaction_hash,
            'timestamp': deposit.order.transaction.timestamp,
            'senderAddress': deposit.order.transaction.sender_address,
            'recipientAddress': deposit.order.transaction.recipient_address,
            'fee': str(deposit.order.transaction.fee),
        }
