from typing import Callable, List
from web3 import Web3
from exchanges.uniswap.v3.models.exact_input_params import ExactInputParams
from exchanges.uniswap.v3.models.quote_exact_input_params import QuoteExactInputParams
from exchanges.uniswap.v3.quoter_v2 import UniswapV3QuoterV2
from exchanges.uniswap.v3.router import UniswapV3Router
from fluffykitten.routes.base_route import BaseRoute
from tokens.base_token import BaseToken


class UniswapV3Route(BaseRoute):
    def __init__(
        self,
        web3: Web3,
        async_web3: Web3,
        name: str,
        quoter_address: str,
        router_address: str,
        path: List[str],
        fees: List[int],
    ):
        super().__init__(web3=web3, async_web3=async_web3, name=name)

        self.quoter = UniswapV3QuoterV2(web3=web3, address=quoter_address)
        self.router = UniswapV3Router(web3=web3, address=router_address)

        assert len(path) >= 2
        self.path = path

        assert len(path) == len(fees) + 1
        self.fees = fees

    def calculate_amount_out(self, amount_in: int) -> int:
        path = list(reversed(self.path))
        fees = list(reversed(self.fees))
        params = QuoteExactInputParams(
            path=path,
            fees=fees,
            amount_in=amount_in,
        )
        quote_exact_input = self.quoter.quote_exact_input(params=params)
        return quote_exact_input.amount_out

    async def exchange(
        self,
        amount_in: int,
        min_amount_out: int = 0,
        gas_limit: int = 200000,
        success_cb: Callable = None,
        failure_cb: Callable = None,
        deadline: int = 99999999999999,
    ):
        tx_fees = await self.transaction_manager.calculate_tx_fees(gas_limit=gas_limit)

        path = list(reversed(self.path))
        fees = list(reversed(self.fees))
        exact_input_params = ExactInputParams(
            path=path,
            fees=fees,
            amount_in=amount_in,
            min_amount_out=min_amount_out,
            recipient=self.web3.eth.default_account,
            deadline=deadline,
        )
        tx_params = self.router.exact_input_single(
            exact_input_params,
            gas_limit=gas_limit,
            max_fee_per_gas=tx_fees.max_fee_per_gas,
            max_priority_fee_per_gas=tx_fees.max_priority_fee_per_gas,
        )

        return await self.transaction_manager.send_transaction(
            tx_params=tx_params,
            success_cb=success_cb,
            failure_cb=failure_cb,
        )
