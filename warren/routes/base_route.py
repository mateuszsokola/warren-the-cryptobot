from typing import Callable, List
from web3 import Web3

from tokens.base_token import BaseToken


class BaseRoute:
    tokens: List[BaseToken] = []

    def __init__(self, web3: Web3, async_web3: Web3, name: str, tokens: List[BaseToken]):
        self.web3 = web3
        self.async_web3 = async_web3
        self.name = name
        self.tokens = tokens

    def assert_tokens(
        self,
        token0: BaseToken,
        token1: BaseToken,
    ) -> List[str]:
        token_names = list(map(lambda token: token.name, self.tokens))

        assert token0.name in token_names
        assert token1.name in token_names

        return token_names

    def calculate_amount_out(self, token0: BaseToken, token1: BaseToken, amount_in: int) -> int:
        pass

    async def exchange(
        self,
        token0: BaseToken,
        token1: BaseToken,
        amount_in: int,
        min_amount_out: int,
        gas_limit: int = 200000,
        success_cb: Callable = None,
        failure_cb: Callable = None,
    ):
        pass
