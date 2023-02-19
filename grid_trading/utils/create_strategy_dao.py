from decimal import Decimal
from grid_trading.models.strategy_dao import BaseStrategyDao, StrategyDao
from grid_trading.models.strategy_status import StrategyStatus
from warren.core.token import Token


def create_base_strategy_dao(order: tuple) -> BaseStrategyDao:
    (id, token0, token1, reference_price, last_tx_price, grid_every_percent, percent_per_flip, status) = order
    return BaseStrategyDao(
        id=id,
        token0=token0,
        token1=token1,
        reference_price=int(reference_price),
        last_tx_price=None if last_tx_price == "None" else int(last_tx_price),
        grid_every_percent=Decimal(grid_every_percent),
        percent_per_flip=Decimal(percent_per_flip),
        status=StrategyStatus[status],
    )


def create_strategy_dao(token: Token, order: tuple) -> StrategyDao:
    (id, token0, token1, reference_price, last_tx_price, grid_every_percent, percent_per_flip, status) = order
    return StrategyDao(
        id=id,
        token0=token.get_token_by_name(token0),
        token1=token.get_token_by_name(token1),
        reference_price=int(reference_price),
        last_tx_price=None if last_tx_price == "None" else int(last_tx_price),
        grid_every_percent=Decimal(grid_every_percent),
        percent_per_flip=Decimal(percent_per_flip),
        status=StrategyStatus[status],
    )
