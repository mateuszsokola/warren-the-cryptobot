from decimal import Decimal
from tokens.base_token import BaseToken
from warren.models.base_model import BaseModel
from .strategy_status import StrategyStatus


class StrategyDto(BaseModel):
    token0: BaseToken
    token1: BaseToken
    reference_price: int
    last_tx_price: int | None
    grid_every_percent: Decimal
    percent_per_flip: Decimal
    status: StrategyStatus
