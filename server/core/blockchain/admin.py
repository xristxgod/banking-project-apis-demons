from sqladmin import ModelView

from core.blockchain import models


class NetworkAdmin(ModelView, model=models.Network):
    can_create = can_edit = True
    can_delete = False

    column_searchable_list = (
        models.Network.name,
        models.Network.short_name,
        models.Network.native_symbol,
        models.Network.family,
        models.Network.is_active,
    )
    column_sortable_list = column_searchable_list
    column_list = (
        models.Network.name,
        models.Network.short_name,
        models.Network.native_symbol,
        models.Network.family,
        models.Network.is_active,
    )
    column_details_list = (
        models.Network.name,
        models.Network.short_name,
        models.Network.native_symbol,
        models.Network.native_decimal_place,
        models.Network.node_url,
        models.Network.is_active,
        models.Network.family,
    )
    form_columns = column_details_list


class StableCoinAdmin(ModelView, model=models.StableCoin):
    can_create = can_edit = can_delete = True
    column_searchable_list = (
        models.StableCoin.name,
        models.StableCoin.symbol,
        models.StableCoin.address,
        models.StableCoin.network,
        models.StableCoin.abi_type,
        models.StableCoin.is_active,
    )
    column_sortable_list = column_searchable_list
    column_list = (
        models.StableCoin.name,
        models.StableCoin.symbol,
        models.StableCoin.address,
        models.StableCoin.network,
        models.StableCoin.is_active,
    )
    column_details_list = (
        models.StableCoin.name,
        models.StableCoin.symbol,
        models.StableCoin.address,
        models.StableCoin.decimal_place,
        models.StableCoin.abi_type,
        models.StableCoin.extra,
        models.StableCoin.is_active,
        models.StableCoin.network,
    )
    form_columns = column_details_list


class OrderProviderAdmin(ModelView, model=models.OrderProvider):
    can_create = can_edit = can_delete = True

    column_searchable_list = (
        models.OrderProvider.address,
        models.OrderProvider.abi_type,
        models.OrderProvider.network,
    )
    column_sortable_list = column_searchable_list
    column_list = (
        models.OrderProvider.address,
        models.OrderProvider.abi_type,
        models.OrderProvider.network,
    )
    column_details_list = (
        models.OrderProvider.address,
        models.OrderProvider.abi_type,
        models.OrderProvider.network,
    )
    form_columns = column_details_list
