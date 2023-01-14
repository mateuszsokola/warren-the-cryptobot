from web3 import Web3
from warren.services.transaction_service import TransactionService

from warren.tokens.base_token import BaseToken


class BaseTokenPair:
    def __init__(
        self,
        web3: Web3,
        async_web3: Web3,
        transaction_service: TransactionService,
        token_in: BaseToken,
        token_out: BaseToken,
    ):
        self.web3 = web3
        self.async_web3 = async_web3
        self.transaction_service = transaction_service
        self.token_in = token_in
        self.token_out = token_out

    async def swap(self, amount_in: int, gas_limit: int = 200000):
        pass

    def balances(self) -> tuple:
        pass

    def quotation(self) -> int:
        pass
