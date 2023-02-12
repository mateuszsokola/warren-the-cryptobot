from decimal import Decimal
from enum import Enum
from tokens.base_token import BaseToken
from warren.models.base_model import BaseModel


class GridTradingOrderStatus(str, Enum):
    active = "Active"
    cancelled = "Cancelled"


class GridTradingOrderDao(BaseModel):
    id: int
    token0: BaseToken
    token1: BaseToken
    buy_delta_trigger: int
    sell_delta_trigger: int
    percent_per_flip: Decimal
    status: GridTradingOrderStatus


class GridTradingOrderDto(BaseModel):
    token0: BaseToken
    token1: BaseToken
    buy_delta_trigger: int
    sell_delta_trigger: int
    percent_per_flip: Decimal
    status: GridTradingOrderStatus
