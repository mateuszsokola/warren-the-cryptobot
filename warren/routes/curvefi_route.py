from typing import Callable, List
from web3 import Web3
from exchanges.curvefi.models.exchange_multiple import ExchangeMultiple
from exchanges.curvefi.models.get_exchange_multiple_amount_params import GetExchangeMultipleAmountParams
from exchanges.curvefi.registry_exchange import CurveFiRegistryExchange
from tokens.base_token import BaseToken
from warren.routes.base_route import BaseRoute
from warren.managers.transaction_manager import TransactionManager
from warren.utils.fill_array_with_null_addresses import fill_array_with_null_addresses


class CurveFiRoute:
    def __init__(
        self,
        web3: Web3,
        async_web3: Web3,
        name: str,
        registry: CurveFiRegistryExchange,
    ):
        self.web3 = web3
        self.async_web3 = async_web3
        self.name = name

        self.transaction_manager = TransactionManager(
            web3=web3,
            async_web3=async_web3,
        )

        self.registry = registry

    def calculate_amount_out(self, token0: BaseToken, token1: BaseToken, amount_in: int) -> int:
        super().assert_tokens(token0, token1)

        routes = []
        route = fill_array_with_null_addresses()

        params = GetExchangeMultipleAmountParams(
            route=route, swap_params=[], amount_in=amount_in, pools=fill_array_with_null_addresses([], len=4)
        )

        amount_out = self.registry.get_exchange_multiple_amount(params)

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

        params = ExchangeMultiple(
            token0=token0.address,
            token1=token1.address,
            amount_in=amount_in,
            min_amount_out=min_amount_out,
            referrer="0x0000000000000000000000000000000000000000",
        )
        tx_params = self.registry.swap(params, tx_fees.gas_limit, tx_fees.max_fee_per_gas, tx_fees.max_fee_per_gas)

        return await self.transaction_manager.send_transaction(
            tx_params=tx_params,
            success_cb=success_cb,
            failure_cb=failure_cb,
        )
