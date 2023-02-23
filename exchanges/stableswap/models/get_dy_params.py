from pydantic import BaseModel


class GetDyParams(BaseModel):
    token0_index: int
    token1_index: int
    amount_in: int
