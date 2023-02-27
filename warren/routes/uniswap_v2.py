from typing import Callable, List
from web3 import Web3
from tokens.base_token import BaseToken
from warren.routes.base_route import BaseRoute
from warren.managers.transaction_manager import TransactionManager

from exchanges.uniswap.v2.models.exact_tokens_for_tokens_params import ExactTokensForTokensParams
from exchanges.uniswap.v2.pair import UniswapV2Pair
from exchanges.uniswap.v2.router import UniswapV2Router


class UniswapV2Route(BaseRoute):
    def __init__(
        self,
        web3: Web3,
        async_web3: Web3,
        name: str,
        pair: UniswapV2Pair,
        router: UniswapV2Router,
        tokens: List[BaseToken],
    ):
        assert len(tokens) == 2

        super().__init__(web3=web3, async_web3=async_web3, name=name, tokens=tokens)

        self.transaction_manager = TransactionManager(
            web3=web3,
            async_web3=async_web3,
        )

        self.pair = pair
        self.router = router

    def calculate_amount_out(self, token0: BaseToken, token1: BaseToken, amount_in: int) -> int:
        token_names = super().assert_tokens(token0, token1)

        if token_names[0] == token0.name:
            return self.pair.calculate_token0_to_token1_amount_out(amount_in=amount_in)
        else:
            return self.pair.calculate_token1_to_token0_amount_out(amount_in=amount_in)

    async def exchange(
        self,
        token0: BaseToken,
        token1: BaseToken,
        amount_in: int,
        min_amount_out: int = 0,
        gas_limit: int = 200000,
        success_cb: Callable = None,
        failure_cb: Callable = None,
    ):
        super().assert_tokens(token0, token1)

        tx_fees = await self.transaction_manager.calculate_tx_fees(gas_limit=gas_limit)

        params = ExactTokensForTokensParams(
            token_in=token0.address,
            token_out=token1.address,
            amount_in=amount_in,
            amount_out_minimum=min_amount_out,
            deadline=9999999999999999,
        )

        tx_params = self.router.swap_exact_tokens_for_tokens(
            params, tx_fees.gas_limit, tx_fees.max_fee_per_gas, tx_fees.max_fee_per_gas
        )

        return await self.transaction_manager.send_transaction(
            tx_params=tx_params,
            success_cb=success_cb,
            failure_cb=failure_cb,
        )
