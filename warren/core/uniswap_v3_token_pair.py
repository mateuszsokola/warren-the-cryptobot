from web3 import Web3
from tokens.base_token import BaseToken
from warren.core.base_token_pair import BaseTokenPair

from exchanges.uniswap.v3.models.exact_input_single_params import ExactInputSingleParams
from exchanges.uniswap.v3.models.quote_exact_input_single_params import (
    QuoteExactInputSingle,
    QuoteExactInputSingleParams,
)
from exchanges.uniswap.v3.pool import UniswapV3Pool
from exchanges.uniswap.v3.quoter_v2 import UniswapV3QuoterV2
from exchanges.uniswap.v3.router import UniswapV3Router
from warren.services.transaction_service import TransactionService


class UniswapV3TokenPair(BaseTokenPair):
    def __init__(
        self,
        web3: Web3,
        async_web3: Web3,
        token0: BaseToken,
        token1: BaseToken,
        name: str,
        pool: UniswapV3Pool,
        quoter: UniswapV3QuoterV2,
        router: UniswapV3Router,
        min_balance_to_transact: int = 0,
    ):
        super().__init__(web3=web3, async_web3=async_web3, name=name, token0=token0, token1=token1)

        self.transaction_service = TransactionService(
            web3=web3,
            async_web3=async_web3,
        )
        self.min_balance_to_transact = min_balance_to_transact

        self.uniswap_v3_pool = pool
        self.uniswap_v3_quoter_v2 = quoter
        self.uniswap_v3_router = router

    def calculate_token0_to_token1_amount_out(self, amount_in: int = int(1 * 10**18)) -> int:
        return self._calculate_amount_out(token_in=self.token0.address, token_out=self.token1.address, amount_in=amount_in)

    def calculate_token1_to_token0_amount_out(self, amount_in: int = int(1 * 10**18)) -> int:
        return self._calculate_amount_out(token_in=self.token1.address, token_out=self.token0.address, amount_in=amount_in)

    async def swap_token0_to_token1(self, amount_in: int, gas_limit: int = 120000):
        return await self._swap(
            token_in=self.token0.address, token_out=self.token1.address, amount_in=amount_in, gas_limit=gas_limit
        )

    async def swap_token1_to_token0(self, amount_in: int, gas_limit: int = 120000):
        return await self._swap(
            token_in=self.token1.address, token_out=self.token0.address, amount_in=amount_in, gas_limit=gas_limit
        )

    def _calculate_amount_out(self, token_in: str, token_out: str, amount_in: int = int(1 * 10**18)) -> int:
        quote_exact_input_single_params = QuoteExactInputSingleParams(
            token_in=token_in,
            token_out=token_out,
            amount_in=amount_in,
            fee=self.uniswap_v3_pool.fee(),
            sqrt_price_limit_x96=0,
        )
        quote_exact_input_single: QuoteExactInputSingle = self.uniswap_v3_quoter_v2.quote_exact_input_single(
            quote_exact_input_single_params
        )

        return quote_exact_input_single.amount_out

    async def _swap(self, token_in: str, token_out: str, amount_in: int, gas_limit: int = 120000):
        tx_fees = await self.transaction_service.calculate_tx_fees(gas_limit=gas_limit)

        exact_input_single_params = ExactInputSingleParams(
            token_in=token_in,
            token_out=token_out,
            fee=self.uniswap_v3_pool.fee(),
            recipient=self.web3.eth.default_account,
            deadline=9999999999999999,
            amount_in=amount_in,
            amount_out_minimum=0,
            sqrt_price_limit_x96=0,
        )

        tx = self.uniswap_v3_router.exact_input_single(
            exact_input_single_params,
            gas_limit=gas_limit,
            max_fee_per_gas=tx_fees.max_fee_per_gas,
            max_priority_fee_per_gas=tx_fees.max_priority_fee_per_gas,
        )

        return await self.transaction_service.send_transaction(tx)
