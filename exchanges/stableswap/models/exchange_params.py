from pydantic import BaseModel


class ExchangeParams(BaseModel):
    token0_index: int
    token1_index: int
    amount_in: int
    min_amount_out: int
