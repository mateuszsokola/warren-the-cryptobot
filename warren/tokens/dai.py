from web3 import Web3
from warren.services.transaction_service import TransactionService
from tokens.base_token import BaseToken

dai_contract_address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"


class Dai(BaseToken):
    def __init__(self, web3: Web3, transaction_service: TransactionService) -> None:
        super().__init__(
            web3=web3,
            transaction_service=transaction_service,
            address=dai_contract_address,
            name="DAI",
        )
