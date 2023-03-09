from fractions import Fraction
from typing import Callable, List
from web3 import Web3
from exchanges.uniswap.v2.factory import UniswapV2Factory
from exchanges.uniswap.v2.models.exact_tokens_for_tokens_params import ExactTokensForTokensParams
from exchanges.uniswap.v2.models.get_pair_params import GetPairParams
from exchanges.uniswap.v2.pair import UniswapV2Pair
from exchanges.uniswap.v2.router import UniswapV2Router
from fluffykitten.routes.base_route import BaseRoute


class UniswapV2Route(BaseRoute):
    def __init__(
        self,
        web3: Web3,
        async_web3: Web3,
        name: str,
        factory_address: str,
        router_address: str,
        path: List[str],
        fees: List[Fraction],
    ):
        super().__init__(web3=web3, async_web3=async_web3, name=name)

        self.factory = UniswapV2Factory(web3=web3, address=factory_address)
        self.router = UniswapV2Router(web3=web3, address=router_address)

        assert len(path) >= 2
        self.path = path

        assert len(path) == len(fees) + 1
        self.fees = fees

        self._process_pairs()

    def calculate_amount_out(self, amount_in: int) -> int:
        amount_out = amount_in

        for pair in self.pairs:
            if pair.pair_inverted == True:
                amount_out = pair.calculate_token1_to_token0_amount_out(amount_in=amount_out)
            else:
                amount_out = pair.calculate_token0_to_token1_amount_out(amount_in=amount_out)

        return amount_out

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

        exact_tokens_for_tokens_params = ExactTokensForTokensParams(
            path=self.path,
            amount_in=amount_in,
            amount_out_minimum=min_amount_out,
            deadline=deadline,
            recipient=self.web3.eth.default_account,
        )
        tx_params = self.router.swap_exact_tokens_for_tokens(
            exact_tokens_for_tokens_params, tx_fees.gas_limit, tx_fees.max_fee_per_gas, tx_fees.max_fee_per_gas
        )

        return await self.transaction_manager.send_transaction(
            tx_params=tx_params,
            success_cb=success_cb,
            failure_cb=failure_cb,
        )

    def _process_pairs(self):
        self.pairs: List[UniswapV2Pair] = []

        for i in range(0, len(self.fees), 1):
            token0 = self.path[i]
            token1 = self.path[i + 1]

            uniswap_v2_pair = self.factory.get_pair(
                params=GetPairParams(token0=token0, token1=token1),
                fee=self.fees[i],
            )
            self.pairs.append(uniswap_v2_pair)
