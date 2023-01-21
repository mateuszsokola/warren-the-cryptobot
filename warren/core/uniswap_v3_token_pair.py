from web3 import Web3
from warren.tokens.base_token import BaseToken
from warren.services.base_token_pair import BaseTokenPair
from warren.services.transaction_service import TransactionService

from warren.uniswap.v3.models.exact_input_single_params import ExactInputSingleParams
from warren.uniswap.v3.models.quote_exact_input_single_params import (
    QuoteExactInputSingle,
    QuoteExactInputSingleParams,
)
from warren.uniswap.v3.pool import UniswapV3Pool
from warren.uniswap.v3.quoter_v2 import UniswapV3QuoterV2
from warren.uniswap.v3.router import UniswapV3Router


class UniswapV3TokenPair(BaseTokenPair):
    def __init__(
        self, web3: Web3, async_web3: Web3, transaction_service: TransactionService, token_in: BaseToken, token_out: BaseToken
    ):
        super().__init__(
            web3,
            async_web3,
            transaction_service,
            token_in=token_in,
            token_out=token_out,
        )

        self.uniswap_v3_pool = UniswapV3Pool(web3)
        self.uniswap_v3_quoter_v2 = UniswapV3QuoterV2(web3)
        self.uniswap_v3_router = UniswapV3Router(web3=web3, transaction_service=transaction_service)

    async def swap(self, amount_in: int, gas_limit: int = 200000):
        tx_fees = await self.transaction_service.calculate_tx_fees(gas_limit=gas_limit)

        exact_input_single_params = ExactInputSingleParams(
            token_in=self.token_in.address,
            token_out=self.token_out.address,
            fee=self.uniswap_v3_pool.fee(),
            recipient=self.web3.eth.default_account,
            deadline=9999999999999999,
            amount_in=amount_in,
            amount_out_minimum=0,
            sqrt_price_limit_x96=0,
        )

        tx = self.uniswap_v3_router.exact_input_single(
            exact_input_single_params,
            gas_limit=tx_fees.gas_limit,
            max_fee_per_gas=tx_fees.max_fee_per_gas,
            max_priority_fee_per_gas=tx_fees.max_priority_fee_per_gas,
        )

        return await self.transaction_service.send_transaction(tx)

    def balances(self):
        token_in_balance = self.token_in.balance_of(self.web3.eth.default_account)
        token_out_balance = self.token_out.balance_of(self.web3.eth.default_account)

        return (token_in_balance, token_out_balance)

    def quote(self):
        quote_exact_input_single_params = QuoteExactInputSingleParams(
            token_in=self.token_in.address,
            token_out=self.token_out.address,
            amount_in=int(1 * 10**18),
            fee=self.uniswap_v3_pool.fee(),
            sqrt_price_limit_x96=0,
        )
        quote_exact_input_single: QuoteExactInputSingle = self.uniswap_v3_quoter_v2.quote_exact_input_single(
            quote_exact_input_single_params
        )

        return quote_exact_input_single.amount_out
