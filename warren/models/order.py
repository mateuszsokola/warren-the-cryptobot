from decimal import Decimal
from enum import Enum
from pydantic import BaseModel
from warren.models.token_pair import TokenPair


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
    token_pair: TokenPair
    trigger_price: int
    percent: Decimal
    status: OrderStatus


class OrderDto(BaseModel):
    type: OrderType
    token_pair: TokenPair
    trigger_price: int
    percent: Decimal
    status: OrderStatus
