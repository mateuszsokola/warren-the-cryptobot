from pydantic import BaseModel
from exchanges.curvefi.models.swap_type import SwapType


class Swap(BaseModel):
    token: str
    pool: str
    swap_type: SwapType
