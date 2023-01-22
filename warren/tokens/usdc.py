from web3 import Web3
from warren.services.transaction_service import TransactionService
from warren.tokens.base_token import BaseToken

usdc_contract_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"


class UsdC(BaseToken):
    def __init__(self, web3: Web3, transaction_service: TransactionService) -> None:
        super().__init__(
            web3=web3,
            transaction_service=transaction_service,
            address=usdc_contract_address,
            name="USDC",
        )

    @staticmethod
    def decimals() -> int:
        return 6
