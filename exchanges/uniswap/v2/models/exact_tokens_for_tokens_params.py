from typing import List
from pydantic import BaseModel


class ExactTokensForTokensParams(BaseModel):
    path: List[str]
    amount_in: int
    amount_out_minimum: int
    deadline: int
    # recipient
    recipient: str
