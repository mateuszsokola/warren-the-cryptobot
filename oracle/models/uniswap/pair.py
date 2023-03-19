from pydantic import BaseModel


class UniswapV2PairDao(BaseModel):
    id: int
    type: str
    address: str
    token0: str
    token1: str
    reserve0: str
    reserve1: str
    timestamp: str


class UniswapV2PairDto(BaseModel):
    type: str
    address: str
    token0: str
    token1: str
    reserve0: str
    reserve1: str
    timestamp: str
