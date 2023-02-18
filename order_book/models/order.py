from decimal import Decimal
from enum import Enum
from tokens.base_token import BaseToken
from warren.models.base_model import BaseModel


class OrderStatus(str, Enum):
    active = "Active"
    executed = "Executed"
    cancelled = "Cancelled"


class OrderType(str, Enum):
    stop_loss = "Stop Loss"
    take_profit = "Take Profit"


class OrderDao(BaseModel):
    id: int
    type: OrderType
    token0: BaseToken
    token1: BaseToken
    trigger_price: int
    percent: Decimal
    status: OrderStatus


class OrderDto(BaseModel):
    type: OrderType
    token0: BaseToken
    token1: BaseToken
    trigger_price: int
    percent: Decimal
    status: OrderStatus
