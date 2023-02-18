import asyncio
import functools
from web3 import Web3
from grid_trading.models.order import GridTradingOrderStatus, grid_trading_order_dao_factory
from grid_trading.utils.create_grid import create_grid
from warren.core.database import Database
from warren.core.token import Token
from warren.core.router import Router
from warren.managers.exchange_manager import ExchangeManager
from warren.utils.logger import logger


class GridTradingService:
    def __init__(self, async_web3: Web3, web3: Web3, database: Database):
        self.async_web3 = async_web3
        self.web3 = web3
        self.database = database
        self.token = Token(
            async_web3=async_web3,
            web3=web3,
        )
        self.router = Router(async_web3=async_web3, web3=web3, token=self.token)

        self.latest_checked_block = 0

    # TODO(mateu.sh): move gas limit to config
    async def find_opportunities(self, gas_limit: int = 200000):
        strategy_list = self.database.list_grid_trading_orders(
            func=functools.partial(grid_trading_order_dao_factory, self.token), status=GridTradingOrderStatus.active
        )
        if len(strategy_list) == 0:
            return

        latest_block = await self.async_web3.eth.get_block("latest")
        if latest_block["number"] == self.latest_checked_block:
            return

        for strategy in strategy_list:
            token0_balance = strategy.token0.balance_of(self.web3.eth.default_account)
            token1_balance = strategy.token1.balance_of(self.web3.eth.default_account)

            last_price = strategy.reference_price if strategy.last_tx_price is None else int(strategy.last_tx_price)
            (lower_limit, upper_limit) = create_grid(last_price, strategy.grid_every_percent)

            exchanges = self.router.get_token_pair_by_token0_and_token1(strategy.token0, strategy.token1)
            # TODO(mateu.sh): i don't like it returns so many values and tuples
            exchange_manager = ExchangeManager(exchange_list=exchanges, token0=strategy.token0, token1=strategy.token1)

            # TODO(mateu.sh): Add min tx value
            # TODO(mateu.sh): Hook min_token_balance_per_tx rather than 0
            # sell tokens
            if exchange_manager.highest_price[2] >= upper_limit and token0_balance > 0:
                amount_in = int(token0_balance * strategy.percent_per_flip)

                try:
                    # TODO(mateu.sh): refactor to accept callback for success and failure
                    await exchange_manager.highest_price[0].swap_token0_to_token1(amount_in=amount_in, gas_limit=gas_limit)
                    self.database.change_grid_trading_order_last_tx_price(strategy.id, exchange_manager.highest_price[2])
                    logger.info(f"[GRID] Sell order #{strategy.id} has been executed at price {exchange_manager.highest_price[2]}")
                except Exception as e:
                    raise e

            # buy tokens
            elif exchange_manager.lowest_price[2] <= lower_limit and token1_balance > 0:
                amount_in = int(token1_balance * strategy.percent_per_flip)

                try:
                    await exchange_manager.lowest_price[0].swap_token1_to_token0(amount_in=amount_in, gas_limit=gas_limit)
                    self.database.change_grid_trading_order_last_tx_price(strategy.id, exchange_manager.lowest_price[2])
                    logger.info(f"[GRID] Buy order #{strategy.id} has been executed at price {exchange_manager.lowest_price[2]}")
                except Exception as e:
                    raise e

            else:
                await asyncio.sleep(0)

        self.latest_checked_block = latest_block["number"]
