from typing import List
from pydantic import BaseModel
from exchanges.uniswap.v2.factory import UniswapV2Factory
from exchanges.uniswap.v2.router import UniswapV2Router
from exchanges.uniswap.v3.pool import UniswapV3Pool
from exchanges.uniswap.v3.router import UniswapV3Router
from exchanges.uniswap.v3.quoter import UniswapV3Quoter
from warren.models.token_pair import BaseTokenPairMetaV2, UniswapV2TokenPairMeta


class BaseExchange(BaseModel):
    name: str
    token_pairs: List[BaseTokenPairMetaV2]


class UniswapV2Exchange(BaseExchange):
    uniswap_v2_factory: UniswapV2Factory
    uniswap_v2_router: UniswapV2Router
    token_pairs: List[UniswapV2TokenPairMeta]


class UniswapV3Exchange(BaseExchange):
    uniswap_v3_pool: UniswapV3Pool
    uniswap_v3_router: UniswapV3Router
    uniswap_v3_quoter: UniswapV3Quoter

