from decimal import Decimal
from enum import Enum
from tokens.base_token import BaseToken
from warren.core.token import Token
from warren.models.base_model import BaseModel


class GridTradingOrderStatus(str, Enum):
    active = "Active"
    cancelled = "Cancelled"


class GridTradingOrderDao(BaseModel):
    id: int
    token0: BaseToken
    token1: BaseToken
    reference_price: int
    last_tx_price: int | None
    grid_every_percent: Decimal
    percent_per_flip: Decimal
    status: GridTradingOrderStatus


class GridTradingHeadlessOrderDao(GridTradingOrderDao):
    token0: str
    token1: str


class GridTradingOrderDto(BaseModel):
    token0: BaseToken
    token1: BaseToken
    reference_price: int
    last_tx_price: int | None
    grid_every_percent: Decimal
    percent_per_flip: Decimal
    status: GridTradingOrderStatus


def grid_trading_order_dao_factory(token: Token, order: tuple) -> GridTradingOrderDao:
    (id, token0, token1, reference_price, last_tx_price, grid_every_percent, percent_per_flip, status) = order
    return GridTradingOrderDao(
        id=id,
        token0=token.get_token_by_name(token0),
        token1=token.get_token_by_name(token1),
        reference_price=int(reference_price),
        last_tx_price=None if last_tx_price == "None" else int(last_tx_price),
        grid_every_percent=Decimal(grid_every_percent),
        percent_per_flip=Decimal(percent_per_flip),
        status=GridTradingOrderStatus[status],
    )


def grid_trading_headless_order_dao_factory(order: tuple) -> GridTradingHeadlessOrderDao:
    (id, token0, token1, reference_price, last_tx_price, grid_every_percent, percent_per_flip, status) = order
    return GridTradingOrderDao(
        id=id,
        token0=token0,
        token1=token1,
        reference_price=int(reference_price),
        last_tx_price=None if last_tx_price == "None" else int(last_tx_price),
        grid_every_percent=Decimal(grid_every_percent),
        percent_per_flip=Decimal(percent_per_flip),
        status=GridTradingOrderStatus[status],
    )
