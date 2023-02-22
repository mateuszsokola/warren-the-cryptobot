from typing import Callable, List
from web3 import Web3
from tokens.base_token import BaseToken
from warren.routes.base_route import BaseRoute
from warren.managers.transaction_manager import TransactionManager

from exchanges.stableswap.models.exchange_params import ExchangeParams
from exchanges.stableswap.models.get_dy_params import GetDyParams
from exchanges.stableswap.tripool import StableSwap3pool


class StableSwap3poolRoute(BaseRoute):
    def __init__(
        self,
        web3: Web3,
        async_web3: Web3,
        name: str,
        pool: StableSwap3pool,
        tokens: List[BaseToken],
    ):
        super().__init__(web3=web3, async_web3=async_web3, name=name, tokens=tokens)

        self.transaction_manager = TransactionManager(
            web3=web3,
            async_web3=async_web3,
        )

        self.pool = pool

    def calculate_amount_out(self, token0: BaseToken, token1: BaseToken, amount_in: int) -> int:
        token_names = super().assert_tokens(token0, token1)

        params = GetDyParams(
            token0_index=token_names.index(token0.name),
            token1_index=token_names.index(token1.name),
            amount_in=amount_in,
        )
        amount_out = self.pool.get_dy(params=params)

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
        token_names = super().assert_tokens(token0, token1)

        tx_fees = await self.transaction_manager.calculate_tx_fees(gas_limit=gas_limit)

        params = ExchangeParams(
            token0_index=token_names.index(token0.name),
            token1_index=token_names.index(token1.name),
            amount_in=amount_in,
            min_amount_out=min_amount_out,
        )

        tx_params = self.pool.exchange(params, tx_fees.gas_limit, tx_fees.max_fee_per_gas, tx_fees.max_fee_per_gas)

        return await self.transaction_manager.send_transaction(
            tx_params=tx_params,
            success_cb=success_cb,
            failure_cb=failure_cb,
        )
