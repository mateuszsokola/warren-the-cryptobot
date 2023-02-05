import asyncio
from typing import List
from web3 import Web3
from warren.core.base_token_pair import BaseTokenPair
from warren.core.database import Database
from warren.models.order import OrderStatus, OrderType
from warren.utils.logger import logger


class OrderBookService:
    def __init__(self, async_web3: Web3, web3: Web3, database: Database, token_routes: dict[str, List[BaseTokenPair]]):
        self.async_web3 = async_web3
        self.web3 = web3
        self.database = database
        self.token_routes = token_routes

        self.latest_checked_block = 0

    async def seek_for_opportunities(self):
        order_list = self.database.list_orders(status=OrderStatus.active)
        if len(order_list) == 0:
            return

        latest_block = await self.async_web3.eth.get_block("latest")
        if latest_block["number"] == self.latest_checked_block:
            return

        for order in order_list:
            exchanges = self.token_routes[order.token_pair]

            token0_balance = 0
            token1_balance = 0

            for exchange in exchanges:
                current_price = exchange.quote()

                if order.type.value == OrderType["stop_loss"].value and current_price <= order.trigger_price:
                    amount_in = int(token_in_balance * order.percent)
                elif order.type.value == OrderType["take_profit"].value and current_price >= order.trigger_price:
                    amount_in = int(token_in_balance * order.percent)
                else:
                    await asyncio.sleep(0)
                    continue

                try:
                    await exchange.swap(amount_in=amount_in)
                    self.database.change_order_status(id=order.id, status=OrderStatus.executed)
                    logger.info(f"Order #{order.id} has been executed")
                except Exception as e:
                    raise e

        self.latest_checked_block = latest_block["number"]
