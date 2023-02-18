from decimal import Decimal
from enum import Enum
from tokens.base_token import BaseToken
from warren.core.token import Token
from warren.models.base_model import BaseModel


class OrderBookOrderStatus(str, Enum):
    active = "Active"
    executed = "Executed"
    cancelled = "Cancelled"


class OrderBookOrderType(str, Enum):
    stop_loss = "Stop Loss"
    take_profit = "Take Profit"


class OrderBookOrderDao(BaseModel):
    id: int
    type: OrderBookOrderType
    token0: BaseToken
    token1: BaseToken
    trigger_price: int
    percent: Decimal
    status: OrderBookOrderStatus


class OrderBookHeadlessOrderDao(OrderBookOrderDao):
    token0: str
    token1: str


class OrderBookOrderDto(BaseModel):
    type: OrderBookOrderType
    token0: BaseToken
    token1: BaseToken
    trigger_price: int
    percent: Decimal
    status: OrderBookOrderStatus


def order_book_order_dao_factory(token: Token, order: tuple) -> OrderBookOrderDao:
    (id, order_type, token0, token1, trigger_price, percent, status) = order
    return OrderBookOrderDao(
        id=id,
        type=OrderBookOrderType[order_type],
        token0=token.get_token_by_name(token0),
        token1=token.get_token_by_name(token1),
        trigger_price=int(trigger_price),
        percent=Decimal(percent),
        status=OrderBookOrderStatus[status],
    )


def order_book_headless_order_dao_factory(order: tuple) -> OrderBookHeadlessOrderDao:
    (id, order_type, token0, token1, trigger_price, percent, status) = order
    return OrderBookOrderDao(
        id=id,
        type=OrderBookOrderType[order_type],
        token0=token0,
        token1=token1,
        trigger_price=int(trigger_price),
        percent=Decimal(percent),
        status=OrderBookOrderStatus[status],
    )
