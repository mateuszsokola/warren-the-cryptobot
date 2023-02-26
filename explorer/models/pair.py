from pydantic import BaseModel


class PairDao(BaseModel):
    id: int
    type: str
    address: str
    token0: str
    token1: str


class PairDto(BaseModel):
    type: str
    address: str
    token0: str
    token1: str
