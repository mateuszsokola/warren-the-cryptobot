import asyncio
import functools
from typing import List
from web3 import Web3
from web3.types import TxReceipt
from order_book.models.order_dao import OrderDao
from order_book.models.order_status import OrderStatus
from order_book.models.order_type import OrderType
from order_book.utils.create_order_dao import create_order_dao
from warren.core.database import Database
from warren.core.token import Token
from warren.core.router import Router
from warren.utils.logger import logger


def success_callback(database: Database, order_id: int, tx: TxReceipt):
    database.change_order_status(id=order_id, status=OrderStatus.executed)
    logger.info(f"ORDER BOOK | Order #{order_id} has been executed. TX #{tx.transactionHash.hex()}")


class OrderBookService:
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

    async def find_opportunities(self, gas_limit: int = 500000):
        order_list: List[OrderDao] = self.database.list_orders(
            func=functools.partial(create_order_dao, self.token), status=OrderStatus.active
        )
        if len(order_list) == 0:
            return

        latest_block = await self.async_web3.eth.get_block("latest")
        if latest_block["number"] == self.latest_checked_block:
            return

        for order in order_list:
            # TODO(mateu.sh): auto cancel order when empty balance
            token0_balance = order.token0.balance_of(self.web3.eth.default_account)

            highest_price_route = None
            highest_price: int = 0
            lowest_price: int = 9999999 * 10 ** order.token1.decimals()

            routes = self.router.get_routes_by_token0_and_token1(order.token0, order.token1)
            for route in routes:
                route_price = route.calculate_amount_out(
                    order.token0, order.token1, amount_in=int(1 * 10 ** order.token0.decimals())
                )

                if highest_price < route_price:
                    highest_price_route = route
                    highest_price = route_price

                if lowest_price > route_price:
                    lowest_price = route_price

            route = None

            if order.type.value == OrderType["buy"].value and highest_price <= order.trigger_price:
                amount_in = int(token0_balance * order.percent)
                route = highest_price_route
            elif order.type.value == OrderType["sell"].value and highest_price >= order.trigger_price:
                amount_in = int(token0_balance * order.percent)
                route = highest_price_route
            elif order.type.value == OrderType["stop_loss"].value and lowest_price <= order.trigger_price:
                amount_in = int(token0_balance * order.percent)
                route = highest_price_route
            elif order.type.value == OrderType["take_profit"].value and highest_price >= order.trigger_price:
                amount_in = int(token0_balance * order.percent)
                route = highest_price_route
            else:
                await asyncio.sleep(0)
                continue

            try:
                await route.exchange(
                    token0=order.token0,
                    token1=order.token1,
                    amount_in=amount_in,
                    min_amount_out=0,
                    gas_limit=gas_limit,
                    success_cb=functools.partial(success_callback, self.database, order.id),
                    failure_cb=None,
                )
            except Exception as e:
                raise e

        self.latest_checked_block = latest_block["number"]
