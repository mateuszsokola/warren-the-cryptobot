from typing import List
from warren.models.base_model import BaseModel


"""
@link https://github.com/curvefi/curve-pool-registry/blob/0bdb116024ccacda39295bb3949c3e6dd0a8e2d9/contracts/Swaps.vy#L872
"""


class ExchangeMultiple(BaseModel):
    """
    Array of [initial token, pool, token, pool, token, ...]
    The array is iterated until a pool address of 0x00, then the last
    given token is transferred to `_receiver`
    """

    route: List[str]
    """
    Multidimensional array of [i, j, swap type] where i and j are the correct
    values for the n'th pool in `_route`.
    """
    swap_params: List[List[int]]
    """
    amount The amount of `_route[0]` token to be sent.
    """
    amount_in: int
    """
    amount out
    """
    min_amount_out: int
