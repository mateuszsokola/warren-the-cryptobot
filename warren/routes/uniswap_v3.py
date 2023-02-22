from typing import Callable, List
from web3 import Web3
from exchanges.uniswap.v3.models.exact_input_single_params import ExactInputSingleParams
from exchanges.uniswap.v3.models.quote_exact_input_single_params import (
    QuoteExactInputSingle,
    QuoteExactInputSingleParams,
)
from exchanges.uniswap.v3.pool import UniswapV3Pool
from exchanges.uniswap.v3.quoter_v2 import UniswapV3QuoterV2
from exchanges.uniswap.v3.router import UniswapV3Router
from tokens.base_token import BaseToken
from warren.routes.base_route import BaseRoute
from warren.managers.transaction_manager import TransactionManager


class UniswapV3Route(BaseRoute):
    def __init__(
        self,
        web3: Web3,
        async_web3: Web3,
        name: str,
        pool: UniswapV3Pool,
        quoter: UniswapV3QuoterV2,
        router: UniswapV3Router,
        tokens: List[BaseToken],
    ):
        assert len(tokens) == 2

        super().__init__(web3=web3, async_web3=async_web3, name=name, tokens=tokens)

        self.transaction_manager = TransactionManager(
            web3=web3,
            async_web3=async_web3,
        )

        self.pool = pool
        self.quoter = quoter
        self.router = router

    def calculate_amount_out(self, token0: BaseToken, token1: BaseToken, amount_in: int) -> int:
        super().assert_tokens(token0, token1)

        quote_exact_input_single_params = QuoteExactInputSingleParams(
            token_in=token0.address,
            token_out=token1.address,
            amount_in=amount_in,
            fee=self.pool.fee(),
            sqrt_price_limit_x96=0,
        )
        quote_exact_input_single: QuoteExactInputSingle = self.quoter.quote_exact_input_single(quote_exact_input_single_params)

        return quote_exact_input_single.amount_out

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

        exact_input_single_params = ExactInputSingleParams(
            token_in=token0.address,
            token_out=token1.address,
            fee=self.pool.fee(),
            recipient=self.web3.eth.default_account,
            deadline=9999999999999999,
            amount_in=amount_in,
            amount_out_minimum=min_amount_out,
            sqrt_price_limit_x96=0,
        )

        tx_params = self.router.exact_input_single(
            exact_input_single_params,
            gas_limit=gas_limit,
            max_fee_per_gas=tx_fees.max_fee_per_gas,
            max_priority_fee_per_gas=tx_fees.max_priority_fee_per_gas,
        )

        return await self.transaction_manager.send_transaction(
            tx_params=tx_params,
            success_cb=success_cb,
            failure_cb=failure_cb,
        )
