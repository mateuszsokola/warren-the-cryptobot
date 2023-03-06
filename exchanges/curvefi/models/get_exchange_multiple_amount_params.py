from typing import List
from warren.models.base_model import BaseModel


class GetExchangeMultipleAmountParams(BaseModel):
    """
    @link https://github.com/curvefi/curve-pool-registry/blob/0bdb116024ccacda39295bb3949c3e6dd0a8e2d9/contracts/Swaps.vy#L872
    """

    """
    Array of [initial token, pool, token, pool, token, ...]
    The array is iterated until a pool address of 0x00, then the last
    given token is transferred to `_receiver`
    """
    route: List[str]

    """
    Multidimensional array of [i, j, swap type] where i and j are the correct
    values for the n'th pool in `_route`. The swap type should be
    1 for a stableswap `exchange`,
    2 for stableswap `exchange_underlying`,
    3 for a cryptoswap `exchange`,
    4 for a cryptoswap `exchange_underlying`,
    5 for factory metapools with lending base pool `exchange_underlying`,
    6 for factory crypto-meta pools underlying exchange (`exchange` method in zap),
    7-11 for wrapped coin (underlying for lending pool) -> LP token "exchange" (actually `add_liquidity`),
    12-14 for LP token -> wrapped coin (underlying for lending or fake pool) "exchange" (actually `remove_liquidity_one_coin`)
    15 for WETH -> ETH "exchange" (actually deposit/withdraw)    
    """
    swap_params: List[List[int]]

    """
    amount The amount of `_route[0]` token to be sent.
    """
    amount_in: int

    """
    Array of pools for swaps via zap contracts. This parameter is only needed for
    Polygon meta-factories underlying swaps.
    """
    pools: List[str] | None
