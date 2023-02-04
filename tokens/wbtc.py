from web3 import Web3
from warren.services.transaction_service import TransactionService
from tokens.base_token import BaseToken


class WBTC(BaseToken):
    def __init__(self, web3: Web3, transaction_service: TransactionService, address: str) -> None:
        super().__init__(
            web3=web3,
            address=address,
            name="WBTC",
        )

    @staticmethod
    def decimals() -> int:
        return 8
