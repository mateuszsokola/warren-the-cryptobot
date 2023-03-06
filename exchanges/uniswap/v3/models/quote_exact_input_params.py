from typing import List
from pydantic import BaseModel


class QuoteExactInputParams(BaseModel):
    # list of tokens
    path: List[str]
    # list of fees
    fees: List[int]
    # amount in
    amount_in: int


class QuoteExactInput(BaseModel):
    amount_out: int
    sqrt_price_limit_x96_after_list: List[int]
    initialized_ticks_crossed_list: List[int]
    gas_estimate: int
