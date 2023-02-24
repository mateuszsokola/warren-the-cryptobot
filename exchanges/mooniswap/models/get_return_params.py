from pydantic import BaseModel


class GetReturnParams(BaseModel):
    token0: str
    token1: str
    amount_in: int
