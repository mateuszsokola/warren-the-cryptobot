import asyncio
from web3 import Web3
from warren.core.create_token_pair import create_token_pair
from warren.core.database import Database
from warren.models.order import OrderStatus, OrderType
from warren.services.transaction_service import TransactionService
from warren.utils.logger import logger


class OrderBookService:
    def __init__(
        self,
        async_web3: Web3,
        web3: Web3,
        database: Database,
        transaction_service: TransactionService,
    ):
        self.async_web3 = async_web3
        self.web3 = web3
        self.transaction_service = transaction_service
        self.database = database

        self.latest_checked_block = 0

    async def seek_for_opportunities(self):
        order_list = self.database.list_orders(status=OrderStatus.active)
        if len(order_list) == 0:
            return

        latest_block = await self.async_web3.eth.get_block("latest")
        if latest_block["number"] == self.latest_checked_block:
            return

        for order in order_list:
            token_pair = create_token_pair(
                async_web3=self.async_web3,
                web3=self.web3,
                transaction_service=self.transaction_service,
                token_pair=order.token_pair,
            )

            current_price = token_pair.quote()
            (
                token_in_balance,
                token_out_balance,
            ) = token_pair.balances()

            if order.type.value == OrderType["stop_loss"].value and current_price <= order.trigger_price:
                amount_in = int(token_in_balance * order.percent)
            elif order.type.value == OrderType["take_profit"].value and current_price >= order.trigger_price:
                amount_in = int(token_in_balance * order.percent)
            else:
                await asyncio.sleep(0)
                continue

            try:
                await token_pair.swap(amount_in=amount_in)
                self.database.change_order_status(id=order.id, status=OrderStatus.executed)
                logger.info(f"Order #{order.id} has been executed")
            except Exception as e:
                raise e

        self.latest_checked_block = latest_block["number"]
