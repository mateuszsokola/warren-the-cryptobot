from web3 import Web3
from warren.services.transaction_service import TransactionService
from warren.tokens.base_token import BaseToken

wbtc_contract_address = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"


class WBtc(BaseToken):
    def __init__(self, web3: Web3, transaction_service: TransactionService) -> None:
        super().__init__(
            web3=web3,
            transaction_service=transaction_service,
            address=wbtc_contract_address,
            name="WBTC",
        )

    @staticmethod
    def decimals() -> int:
        return 8
