from typing import Optional

from tortoise.queryset import QuerySet

from apps.telegram.models import Language, TelegramAppsType, TelegramText


class Text:
    def __init__(self, objs: QuerySet[TelegramText]):
        self.objs = objs

    async def get(self, pk: str, lang: Optional[Language] = None):
        if not lang:
            lang = await Language.default()

        return await self.objs.get(
            pk=pk
        ).values_list(
            f'text_{lang.tag}',
            flat=True,
        )


class TelegramTextFactory:
    model = TelegramText

    class TypeNotFound(Exception):
        pass

    @classmethod
    async def get(cls, typ: TelegramAppsType) -> Text:
        qs = cls.model.filter(apps_type=typ)
        if not await qs.exists():
            raise cls.TypeNotFound()
        return Text(await qs.all())
