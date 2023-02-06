from typing import Any
from web3 import Web3


class UniswapV3BaseQuoter:
    def __init__(self, web3: Web3, address: str):
        self.web3 = web3
        self.address = address

    def quote_exact_input_single(self, params: Any) -> int:
        pass
