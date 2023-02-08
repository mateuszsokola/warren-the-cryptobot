from fractions import Fraction

from tokens.base_token import BaseToken
from warren.models.base_model import BaseModel


class Config:
    arbitrary_types_allowed = True


class BaseTokenPairMetaV2(BaseModel):
    name: str
    token0: BaseToken
    token1: BaseToken


class UniswapV2TokenPairMeta(BaseTokenPairMetaV2):
    fee: Fraction
