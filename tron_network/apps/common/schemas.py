from typing import Optional

from pydantic import BaseModel, validator, ValidationError
from mnemonic import Mnemonic


class BodyCreateWallet(BaseModel):
    mnemonic: Optional[str]
    passphrase: Optional[str] = ''

    @validator('mnemonic')
    def valid_mnemonic(cls, value: str):
        obj = Mnemonic('english')
        if not value:
            return obj.generate()
        if not obj.check(value):
            raise ValidationError()
        return value


class ResponseCreateWallet(BodyCreateWallet):
    address: str
    private_key: str
    public_key: str
