from warren.models.pools.base_pool import BasePool


class CurveFiPool(BasePool):
    swap_type: int
    pool_address: str
