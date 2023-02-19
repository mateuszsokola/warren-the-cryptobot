from tokens.base_token import BaseToken
from tokens.dai import DAI
from tokens.usdc import USDC
from tokens.wbtc import WBTC
from tokens.weth9 import WETH9


def get_token_class_by_name(name: str) -> BaseToken:
    if name == "DAI":
        return DAI
    elif name == "USDC":
        return USDC
    elif name == "WBTC":
        return WBTC
    elif name == "WETH9":
        return WETH9
    else:
        return None
