import asyncio
import functools
from decimal import Decimal
from web3 import Web3
from warren.core.database import Database
from warren.core.token import Token
from warren.core.router import Router
from warren.models.order import OrderDao, OrderStatus, OrderType
from warren.utils.logger import logger


# def order_dao_factory(token: Token, order: tuple) -> OrderDao:
#     (id, order_type, token0, token1, trigger_price, percent, status) = order
#     return OrderDao(
#         id=id,
#         type=OrderType[order_type],
#         token0=token.get_token_by_name(token0),
#         token1=token.get_token_by_name(token1),
#         trigger_price=int(trigger_price),
#         percent=Decimal(percent),
#         status=OrderStatus[status],
#     )


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

    async def seek_for_opportunities(self, gas_limit: int = 200000):
        # order_list = self.database.list_orders(func=functools.partial(order_dao_factory, self.token), status=OrderStatus.active)
        # if len(order_list) == 0:
        #     return

        latest_block = await self.async_web3.eth.get_block("latest")
        if latest_block["number"] == self.latest_checked_block:
            return


        self.latest_checked_block = latest_block["number"]
