from typing import Callable
from web3 import Web3

from warren.managers.transaction_manager import TransactionManager


class BaseRoute:
    def __init__(self, web3: Web3, async_web3: Web3, name: str):
        self.web3 = web3
        self.async_web3 = async_web3
        self.name = name
        self.transaction_manager = TransactionManager(
            web3=web3,
            async_web3=async_web3,
        )

    def calculate_amount_out(self, amount_in: int) -> int:
        pass

    async def exchange(
        self,
        amount_in: int,
        min_amount_out: int,
        gas_limit: int = 200000,
        success_cb: Callable = None,
        failure_cb: Callable = None,
    ):
        pass
