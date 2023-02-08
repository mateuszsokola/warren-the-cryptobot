import asyncio
from web3 import Web3
from warren.core.database import Database
from warren.core.router import Router
from warren.models.order import OrderStatus, OrderType
from warren.utils.logger import logger


class OrderBookService:
    def __init__(self, async_web3: Web3, web3: Web3, database: Database):
        self.async_web3 = async_web3
        self.web3 = web3
        self.database = database
        self.router = Router(
            async_web3=async_web3,
            web3=web3,
        )

        self.latest_checked_block = 0

    async def seek_for_opportunities(self):
        order_list = self.database.list_orders(web3=self.web3, status=OrderStatus.active)
        if len(order_list) == 0:
            return

        latest_block = await self.async_web3.eth.get_block("latest")
        if latest_block["number"] == self.latest_checked_block:
            return

        for order in order_list:
            token0_balance = order.token0.balance_of(self.web3.eth.default_account)
            token1_balance = order.token1.balance_of(self.web3.eth.default_account)

            # TODO(mateu.sh): add sell (at highest price) order
            highest_price_exchange = None
            highest_price: int = 0
            highest_amount_in: int = 0
            token1_to_token0: bool = False

            # TODO(mateu.sh): add buy (at lowest price) order
            lowest_price_dex = None
            lowest_price: int = 0
            lowest_amount_in: int = 0

            exchanges = self.router.get_exchange_list()
            for exchange in exchanges:
                a = exchange.token0.name == order.token0.name and exchange.token1.name == order.token1.name
                b = exchange.token0.name == order.token1.name and exchange.token1.name == order.token0.name
                if a or b:
                    exchange_price = (
                        exchange.calculate_token1_to_token0_amount_out() if b else exchange.calculate_token1_to_token0_amount_out()
                    )

                    if highest_price < exchange_price:
                        highest_price_exchange = exchange
                        highest_price = exchange_price
                        highest_amount_in = token0_balance if b else token1_balance
                        token1_to_token0 = b

                    if lowest_price > exchange_price:
                        lowest_price_exchange = exchange
                        lowest_price = exchange_price
                        lowest_amount_in = token0_balance if b else token1_balance

            exchange = None

            # TODO(mateu.sh): refactor those conditional statements
            if order.type.value == OrderType["stop_loss"].value and exchange_price <= order.trigger_price:
                amount_in = int(highest_amount_in * order.percent)
                exchange = highest_price_exchange
            elif order.type.value == OrderType["take_profit"].value and exchange_price >= order.trigger_price:
                amount_in = int(highest_amount_in * order.percent)
                exchange = highest_price_exchange
            else:
                await asyncio.sleep(0)
                continue

            try:
                if token1_to_token0:
                    await exchange.swap_token0_to_token1(amount_in=amount_in, gas_limit=200000)
                else:
                    await exchange.swap_token1_to_token0(amount_in=amount_in, gas_limit=200000)

                self.database.change_order_status(id=order.id, status=OrderStatus.executed)
                logger.info(f"Order #{order.id} has been executed")
            except Exception as e:
                raise e

        self.latest_checked_block = latest_block["number"]
