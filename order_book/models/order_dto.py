from decimal import Decimal
from order_book.models.order_status import OrderStatus
from order_book.models.order_type import OrderType
from tokens.base_token import BaseToken
from warren.models.base_model import BaseModel


class OrderDto(BaseModel):
    type: OrderType
    token0: BaseToken
    token1: BaseToken
    trigger_price: int
    percent: Decimal
    status: OrderStatus
