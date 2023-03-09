from web3 import Web3

from tokens.base_token import BaseToken
from tokens.dai import DAI
from tokens.ldo import LDO
from tokens.link import LINK
from tokens.usdc import USDC
from tokens.usdt import USDT
from tokens.wbtc import WBTC
from tokens.weth9 import WETH9
from tokens.st_eth import stETH


def create_token(web3: Web3, name: str, address: str) -> BaseToken:
    if name == "WETH9":
        return WETH9(web3=web3, address=address)

    if name == "DAI":
        return DAI(web3=web3, address=address)

    elif name == "WBTC":
        return WBTC(web3=web3, address=address)

    elif name == "USDC":
        return USDC(web3=web3, address=address)

    elif name == "USDT":
        return USDT(web3=web3, address=address)

    elif name == "stETH":
        return stETH(web3=web3, address=address)

    elif name == "LDO":
        return LDO(web3=web3, address=address)

    elif name == "LINK":
        return LINK(web3=web3, address=address)

    else:
        return None
