from pydantic import BaseModel


class GetDyParams(BaseModel):
    token0_index: int
    token1_index: str
    amount_in: int
