from enum import Enum


class TokenPair(str, Enum):
    weth9_dai = "WETH9/DAI"
    dai_weth9 = "DAI/WETH9"
