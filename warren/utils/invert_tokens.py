from typing import Tuple
from tokens.base_token import BaseToken


def invert_tokens(token0: BaseToken, token1: BaseToken) -> Tuple[BaseToken, BaseToken]:
    return (token1, token0)
