from web3 import Web3

from tokens.base_token import BaseToken
from tokens.dai import DAI
from tokens.gno import GNO
from tokens.usdc import USDC
from tokens.wbtc import WBTC
from tokens.weth9 import WETH9
from tokens.wxdai import WXDAI


def create_token(web3: Web3, name: str, address: str) -> BaseToken:
    if name == "WETH9":
        return WETH9(web3=web3, address=address)

    if name == "DAI":
        return DAI(web3=web3, address=address)

    elif name == "WBTC":
        return WBTC(web3=web3, address=address)

    elif name == "USDC":
        return USDC(web3=web3, address=address)

    elif name == "GNO":
        return GNO(web3=web3, address=address)

    elif name == "WXDAI":
        return WXDAI(web3=web3, address=address)

    else:
        return None
