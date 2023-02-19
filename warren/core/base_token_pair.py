from typing import Callable
from web3 import Web3

from tokens.base_token import BaseToken


class BaseTokenPair:
    def __init__(self, web3: Web3, async_web3: Web3, name: str, token0: BaseToken, token1: BaseToken):
        self.web3 = web3
        self.async_web3 = async_web3
        self.name = name
        self.token0 = token0
        self.token1 = token1

    def calculate_token0_to_token1_amount_out(self, amount_in: int) -> int:
        pass

    def calculate_token1_to_token0_amount_out(self, amount_in: int) -> int:
        pass

    async def swap_token0_to_token1(
        self,
        amount_in: int,
        gas_limit: int = 120000,
        success_cb: Callable = None,
        failure_cb: Callable = None,
    ):
        pass

    async def swap_token1_to_token0(
        self,
        amount_in: int,
        gas_limit: int = 120000,
        success_cb: Callable = None,
        failure_cb: Callable = None,
    ):
        pass
