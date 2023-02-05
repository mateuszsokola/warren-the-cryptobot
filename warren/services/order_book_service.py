import asyncio
from typing import List
from web3 import Web3
from warren.core.base_token_pair import BaseTokenPair
from warren.core.create_token_pair import create_token_pair
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

            # TODO(mateu.sh): get rid of create_token_pair
            (token0, token1) = create_token_pair(web3=self.web3, token_pair=order.token_pair)

            token0_balance = token0.balance_of(self.web3.eth.default_account)
            token1_balance = token1.balance_of(self.web3.eth.default_account)

            # TODO(mateu.sh): add sell (at highest price) order
            higest_price_exchange = None
            higest_price = 0

            # TODO(mateu.sh): add buy (at lowest price) order
            lowest_price_dex = None
            lowest_price = 0

            for exchange in exchanges:
                exchange_price = (
                    exchange.calculate_token1_to_token0_amount_out()
                    if order.token0_to_token1
                    else exchange.calculate_token1_to_token0_amount_out()
                )

                if higest_price < exchange_price:
                    higest_price_exchange = exchange
                    higest_price = exchange_price

                if lowest_price > exchange_price:
                    lowest_price_exchange = exchange
                    lowest_price = exchange_price

            token_in_amount = token0_balance if order.token0_to_token1 else token1_balance
            exchange = None

            # TODO(mateu.sh): refactor those conditional statements
            if order.type.value == OrderType["stop_loss"].value and exchange_price <= order.trigger_price:
                amount_in = int(token_in_amount * order.percent)
                exchange = higest_price_exchange
            elif order.type.value == OrderType["take_profit"].value and exchange_price >= order.trigger_price:
                amount_in = int(token_in_amount * order.percent)
                exchange = higest_price_exchange
            else:
                await asyncio.sleep(0)
                continue

            try:
                if order.token0_to_token1:
                    await exchange.swap_token0_to_token1(amount_in=amount_in)
                else:
                    await exchange.swap_token1_to_token0(amount_in=amount_in)

                self.database.change_order_status(id=order.id, status=OrderStatus.executed)
                logger.info(f"Order #{order.id} has been executed")
            except Exception as e:
                raise e

        self.latest_checked_block = latest_block["number"]
