from pydantic import BaseModel, Field, AnyUrl

from core.blockchain.models import NetworkFamily


class BodyNetwork(BaseModel):
    name: str
    short_name: str = Field(alias='shortName')
    native_symbol: str = Field(alias='nativeSymbol')
    native_decimal_place: int = Field(alias='nativeDecimalPlace')
    node_url: AnyUrl = Field(alias='nodeUrl')
    family: NetworkFamily
