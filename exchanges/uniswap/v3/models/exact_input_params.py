from typing import List
from pydantic import BaseModel


class ExactInputParams(BaseModel):
    # list of tokens
    path: List[str]
    # list of fees
    fees: List[int]
    # recipient
    recipient: str
    # deadline
    deadline: int
    # amount in
    amount_in: int
    # min amount out
    min_amount_out: int
