from web3 import Web3

from tokens.base_token import BaseToken


class BaseTokenPair:
    def __init__(
        self,
        web3: Web3,
        async_web3: Web3,
    ):
        self.web3 = web3
        self.async_web3 = async_web3

    def calculate_token0_to_token1_amount_out(self, amount_in: int) -> int:
        pass

    def calculate_token1_to_token0_amount_out(self, amount_in: int) -> int:
        pass

    async def swap_token0_to_token1(self, amount_in: int, gas_limit: int = 120000):
        pass

    async def swap_token1_to_token0(self, amount_in: int, gas_limit: int = 120000):
        pass
