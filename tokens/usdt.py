from web3 import Web3
from tokens.base_token import BaseToken


class USDT(BaseToken):
    def __init__(self, web3: Web3, address: str) -> None:
        super().__init__(
            web3=web3,
            address=address,
            name="USDT",
            abi_name="IUSDT.json",
        )
