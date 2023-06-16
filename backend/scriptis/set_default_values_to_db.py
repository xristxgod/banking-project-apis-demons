from typing import Type

from tortoise import Tortoise, models, transactions

import settings
from apps.cryptocurrencies.models import Network, Currency
from apps.telegram.models import TelegramAppsType, Language, TelegramText

cryptocurrencies_fixtures = [
    {
        'table': Network,
        'values': [
            {
                'id': 1,
                'name': 'ETH',
            },
            {
                'id': 2,
                'name': 'BSC',
            }
        ]
    },
    {
        'table': Currency,
        'values': [
            {
                'id': 1,
                'name': 'USDT Token',
                'symbol': 'USDT',
                'address': '0x337610d27c682E347C9cD60BD4b3b107C9d34dDd',
                'decimal_place': 18,
                'network_id': 2,    # BSC
            }
        ]
    }
]

telegram_fixtures = [
    {
        'table': Language,
        'values': [
            {
                'id': 1,
                'name': 'English',
                'short_name': 'ENG',
            },
            {
                'ru': 2,
                'name': 'Русский',
                'short_name': 'RU',
            }
        ]
    },
    {
        'table': TelegramText,
        'values': [
            # Message
            {
                'id': 'registration',
                'apps_type': TelegramAppsType.START,
                'text_ru': 'Регистрация',
                'text_eng': 'Registration',
            },
            {
                'id': 'menu',
                'apps_type': TelegramAppsType.START,
                'text_ru': 'Меню',
                'text_eng': 'Menu',
            },
            {
                'id': 'success_registration',
                'apps_type': TelegramAppsType.START,
                'text_ru': 'Успешно!',
                'text_eng': 'Success!',
            },

            # Button
            {
                'id': 'registration_button',
                'apps_type': TelegramAppsType.START,
                'text_ru': 'Зарегистрироваться',
                'text_eng': 'Registration',
            },
            {
                'id': 'choose_lang_button',
                'apps_type': TelegramAppsType.START,
                'text_ru': 'Изменить язык',
                'text_eng': 'Choose language',
            },
            {
                'id': 'show_balance_button',
                'apps_type': TelegramAppsType.START,
                'text_ru': 'Баланс',
                'text_eng': 'Balance',
            },
            {
                'id': 'deposit_button',
                'apps_type': TelegramAppsType.START,
                'text_ru': 'Пополнить счет',
                'text_eng': 'Deposit',
            },
        ]
    }
]


all_fixtures: list[list] = [
    # cryptocurrencies_fixtures,
    telegram_fixtures,
]


@transactions.atomic()
async def add():
    for fixtures in all_fixtures:
        for fix in fixtures:
            table: Type[models.MODEL] = fix['table']
            await table.bulk_create([
                table(**value)
                for value in fix['values']
            ])


async def main():
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={'models': settings.APPS_MODELS},
    ),
    try:
        await add()
    except Exception as err:
        raise err
    finally:
        await Tortoise.close_connections()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())