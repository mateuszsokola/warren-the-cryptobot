from pydantic import BaseModel

# struct QuoteExactInputSingleParams {
#     address tokenIn;
#     address tokenOut;
#     uint256 amountIn;
#     uint24 fee;
#     uint160 sqrtPriceLimitX96;
# }


class QuoteExactInputSingleParams(BaseModel):
    token_in: str
    token_out: str
    amount_in: int
    fee: int
    sqrt_price_limit_x96: int


# uint256 amountOut,
# uint160 sqrtPriceX96After,
# uint32 initializedTicksCrossed,
# uint256 gasEstimate


class QuoteExactInputSingle(BaseModel):
    amount_out: int
    sqrt_price_limit_x96_after: int
    initialized_ticks_crossed: int
    gas_estimate: int
