from web3 import Web3


class BaseTokenPair:
    def __init__(
        self,
        web3: Web3,
        async_web3: Web3,
    ):
        self.web3 = web3
        self.async_web3 = async_web3

    async def swap(self, amount_in: int, gas_limit: int = 120000):
        pass

    def quote(
        self,
    ) -> int:
        pass
