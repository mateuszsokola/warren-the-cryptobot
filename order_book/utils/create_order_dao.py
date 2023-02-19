from decimal import Decimal
from order_book.models.order_dao import BaseOrderDao, OrderDao
from order_book.models.order_status import OrderStatus
from order_book.models.order_type import OrderType
from warren.core.token import Token


def create_base_order_dao(order: tuple) -> BaseOrderDao:
    (id, order_type, token0, token1, trigger_price, percent, status) = order
    return BaseOrderDao(
        id=id,
        type=OrderType[order_type],
        token0=token0,
        token1=token1,
        trigger_price=int(trigger_price),
        percent=Decimal(percent),
        status=OrderStatus[status],
    )


def create_order_dao(token: Token, order: tuple) -> OrderDao:
    (id, order_type, token0, token1, trigger_price, percent, status) = order
    return OrderDao(
        id=id,
        type=OrderType[order_type],
        token0=token.get_token_by_name(token0),
        token1=token.get_token_by_name(token1),
        trigger_price=int(trigger_price),
        percent=Decimal(percent),
        status=OrderStatus[status],
    )
