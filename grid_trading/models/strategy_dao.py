from decimal import Decimal
from tokens.base_token import BaseToken
from warren.models.base_model import BaseModel
from .strategy_status import StrategyStatus


class BaseStrategyDao(BaseModel):
    id: int
    token0: str
    token1: str
    reference_price: int
    last_tx_price: int | None
    grid_every_percent: Decimal
    percent_per_flip: Decimal
    status: StrategyStatus


class StrategyDao(BaseStrategyDao):
    token0: BaseToken
    token1: BaseToken
