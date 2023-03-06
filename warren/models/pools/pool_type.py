from enum import Enum


class PoolType(str, Enum):
    curvefi = "CurveFi"
    uniswap_v2 = "Uniswap V2"
    uniswap_v3 = "Uniswap V3"
