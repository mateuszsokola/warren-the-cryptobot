from pydantic import BaseModel


class GetPairParams(BaseModel):
    token0: str
    token1: str
