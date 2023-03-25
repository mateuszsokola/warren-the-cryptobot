from pydantic import BaseModel


class SwapcatOffer(BaseModel):
    id: int
    block_number: int
    token0: str
    token1: str
    recipient: str
    amount: int
    available_balance: int


class SwapcatV2Offer(BaseModel):
    id: int
    block_number: int
    token0: str
    token1: str
    recipient: str
    unknown_address: str
    amount: int
    available_balance: int
