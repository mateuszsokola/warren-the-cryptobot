from pydantic import BaseModel


class ExchangeParams(BaseModel):
    token0_index: int
    token1_index: str
    amount_in: int
    min_amount_out: int
