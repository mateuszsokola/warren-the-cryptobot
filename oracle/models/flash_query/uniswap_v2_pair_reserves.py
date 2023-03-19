from pydantic import BaseModel


class UniswapV2PairReserves(BaseModel):
    address: str
    reserve0: int
    reserve1: int
    timestamp: int
