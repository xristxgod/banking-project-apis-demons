from src.settings import settings


class encoder:
    secret_key = settings.ENCODE_SECRET_KEY

    @classmethod
    async def encode(cls, value) -> str:
        raise NotImplementedError()

    @classmethod
    async def decode(cls, value) -> str:
        raise NotImplementedError()
