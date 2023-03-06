from typing import List
from warren.models.base_model import BaseModel
from warren.models.pools.pool_type import PoolType


class BasePool(BaseModel):
    name: str
    type: PoolType
    tokens: List[str]
