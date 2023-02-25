from tokens.base_token import BaseToken
from tokens.dai import DAI
from tokens.ldo import LDO
from tokens.st_eth import stETH
from tokens.usdc import USDC
from tokens.usdt import USDT
from tokens.wbtc import WBTC
from tokens.weth9 import WETH9


def get_token_class_by_name(name: str) -> BaseToken:
    if name == "DAI":
        return DAI
    elif name == "USDC":
        return USDC
    elif name == "USDT":
        return USDT
    elif name == "WBTC":
        return WBTC
    elif name == "WETH9":
        return WETH9
    elif name == "stETH":
        return stETH
    elif name == "LDO":
        return LDO
    else:
        return None
