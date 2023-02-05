from typing import Tuple
from web3 import Web3

from tokens.base_token import BaseToken
from tokens.dai import DAI
from tokens.usdc import USDC
from tokens.wbtc import WBTC
from tokens.weth9 import WETH9

from warren.models.token_pair import TokenPair


def create_token_pair(
    web3: Web3,
    token_pair: TokenPair,
) -> Tuple[BaseToken, BaseToken]:
    if token_pair.value == "WETH9/DAI":
        return (
            WETH9(web3=web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
            DAI(web3=web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F"),
        )

    elif token_pair.value == "WETH9/WBTC":
        return (
            WETH9(web3=web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
            WBTC(web3=web3, address="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"),
        )

    elif token_pair.value == "WETH9/USDC":
        return (
            WETH9(web3=web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
            USDC(web3=web3, address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"),
        )

    else:
        return None
