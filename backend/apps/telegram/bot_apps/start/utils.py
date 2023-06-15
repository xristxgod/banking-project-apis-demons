from apps.telegram.models import TelegramAppsType
from apps.telegram.utils import TelegramTextFactory


# ADD cache function
async def get_app_texts():
    return await TelegramTextFactory.get(typ=TelegramAppsType.START)
