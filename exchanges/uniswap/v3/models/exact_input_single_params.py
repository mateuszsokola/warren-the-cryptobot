from pydantic import BaseModel

# struct ExactInputSingleParams {
#     address tokenIn;
#     address tokenOut;
#     uint24 fee;
#     address recipient;
#     uint256 deadline;
#     uint256 amountIn;
#     uint256 amountOutMinimum;
#     uint160 sqrtPriceLimitX96;
# }


class ExactInputSingleParams(BaseModel):
    token_in: str
    token_out: str
    fee: int
    recipient: str
    deadline: int
    amount_in: int
    amount_out_minimum: int
    sqrt_price_limit_x96: int
