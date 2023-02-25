from pydantic import BaseModel


class SwapParams(BaseModel):
    token0: str
    token1: str
    amount_in: int
    min_amount_out: int
    referrer: str
