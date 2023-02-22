from typing import Callable
from web3 import Web3
from exchanges.uniswap.v2.models.exact_tokens_for_tokens_params import ExactTokensForTokensParams
from tokens.base_token import BaseToken
from warren.core.base_token_pair import BaseTokenPair
from warren.managers.transaction_manager import TransactionManager

from exchanges.uniswap.v2.pair import UniswapV2Pair
from exchanges.uniswap.v2.router import UniswapV2Router


class UniswapV2TokenPair(BaseTokenPair):
    def __init__(
        self,
        web3: Web3,
        async_web3: Web3,
        name: str,
        token0: BaseToken,
        token1: BaseToken,
        token_pair: UniswapV2Pair,
        router: UniswapV2Router,
        min_balance_to_transact: int = 0,
    ):
        super().__init__(web3=web3, async_web3=async_web3, name=name, token0=token0, token1=token1)

        self.transaction_service = TransactionManager(
            web3=web3,
            async_web3=async_web3,
        )
        self.min_balance_to_transact = min_balance_to_transact

        self.uniswap_v2_pair = token_pair
        self.uniswap_v2_router = router

    def calculate_token0_to_token1_amount_out(self, amount_in: int = int(1 * 10**18)) -> int:
        amount_out = self.uniswap_v2_pair.calculate_token0_to_token1_amount_out(amount_in=amount_in)

        return amount_out

    def calculate_token1_to_token0_amount_out(self, amount_in: int = int(1 * 10**18)) -> int:
        amount_out = self.uniswap_v2_pair.calculate_token1_to_token0_amount_out(amount_in=amount_in)

        return amount_out

    async def swap_token0_to_token1(
        self,
        amount_in: int,
        gas_limit: int = 120000,
        success_cb: Callable = None,
        failure_cb: Callable = None,
    ):
        return await self._swap(
            token_in=self.uniswap_v2_pair.token0,
            token_out=self.uniswap_v2_pair.token1,
            amount_in=amount_in,
            gas_limit=gas_limit,
            success_cb=success_cb,
            failure_cb=failure_cb,
        )

    async def swap_token1_to_token0(
        self,
        amount_in: int,
        gas_limit: int = 120000,
        success_cb: Callable = None,
        failure_cb: Callable = None,
    ):
        return await self._swap(
            token_in=self.uniswap_v2_pair.token1,
            token_out=self.uniswap_v2_pair.token0,
            amount_in=amount_in,
            gas_limit=gas_limit,
            success_cb=success_cb,
            failure_cb=failure_cb,
        )

    async def _swap(
        self,
        token_in: str,
        token_out: str,
        amount_in: int,
        gas_limit: int = 120000,
        success_cb: Callable = None,
        failure_cb: Callable = None,
    ):
        tx_fees = await self.transaction_service.calculate_tx_fees(gas_limit=gas_limit)

        params = ExactTokensForTokensParams(
            token_in=token_in,
            token_out=token_out,
            amount_in=amount_in,
            amount_out_minimum=0,
            deadline=9999999999999999,
        )

        tx_params = self.uniswap_v2_router.swap_exact_tokens_for_tokens(
            params, tx_fees.gas_limit, tx_fees.max_fee_per_gas, tx_fees.max_fee_per_gas
        )

        return await self.transaction_service.send_transaction(
            tx_params=tx_params,
            success_cb=success_cb,
            failure_cb=failure_cb,
        )
