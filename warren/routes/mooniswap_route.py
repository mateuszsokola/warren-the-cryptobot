from typing import Callable, List
from web3 import Web3
from tokens.base_token import BaseToken
from warren.routes.base_route import BaseRoute
from warren.managers.transaction_manager import TransactionManager

from exchanges.mooniswap.models.swap_params import SwapParams
from exchanges.mooniswap.models.get_return_params import GetReturnParams
from exchanges.mooniswap.mooniswap import MooniSwap


class MooniswapRoute(BaseRoute):
    def __init__(
        self,
        web3: Web3,
        async_web3: Web3,
        name: str,
        pool: MooniSwap,
        tokens: List[BaseToken],
    ):
        super().__init__(web3=web3, async_web3=async_web3, name=name, tokens=tokens)

        self.transaction_manager = TransactionManager(
            web3=web3,
            async_web3=async_web3,
        )

        self.pool = pool

    def calculate_amount_out(self, token0: BaseToken, token1: BaseToken, amount_in: int) -> int:
        super().assert_tokens(token0, token1)

        params = GetReturnParams(token0=token0.address, token1=token1.address, amount_in=amount_in)
        amount_out = self.pool.get_return(params=params)

        return amount_out

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

        params = SwapParams(
            token0=token0.address,
            token1=token1.address,
            amount_in=amount_in,
            min_amount_out=min_amount_out,
            referrer="0x0000000000000000000000000000000000000000",
        )
        tx_params = self.pool.swap(params, tx_fees.gas_limit, tx_fees.max_fee_per_gas, tx_fees.max_fee_per_gas)

        return await self.transaction_manager.send_transaction(
            tx_params=tx_params,
            success_cb=success_cb,
            failure_cb=failure_cb,
        )
