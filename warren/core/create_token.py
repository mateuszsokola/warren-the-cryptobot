from web3 import Web3

from tokens.base_token import BaseToken
from tokens.weth9 import WETH9


def create_token(
    web3: Web3,
    name: str,
    address: str,
    abi_name: str,
    decimals: int,
    native: bool,
) -> BaseToken:
    if name == "WETH9":
        return WETH9(
            web3=web3,
            address=address,
        )
    else:
        return BaseToken(
            web3=web3,
            address=address,
            name=name,
            abi_name=abi_name,
            decimals=decimals,
            native=native,
        )
