from web3 import Web3
from exchanges.uniswap.v3.base_quoter import UniswapV3BaseQuoter
from exchanges.uniswap.v3.models.quote_exact_input_params import QuoteExactInput, QuoteExactInputParams

from exchanges.uniswap.v3.models.quote_exact_input_single_params import (
    QuoteExactInputSingle,
    QuoteExactInputSingleParams,
)
from exchanges.uniswap.v3.utils.encode_path import encode_path
from warren.utils.load_contract_abi import load_contract_abi

uniswap_v3_quoter_v2_address = "0x61fFE014bA17989E743c5F6cB21bF9697530B21e"


class UniswapV3QuoterV2(UniswapV3BaseQuoter):
    def __init__(self, web3: Web3, address: str):
        self.web3 = web3
        self.address = address
        self.contract = web3.eth.contract(
            address=address,
            abi=load_contract_abi("IQuoterV2.json", "artifacts/uniswap/v3"),
        )

    def quote_exact_input(self, params: QuoteExactInputParams) -> QuoteExactInput:
        path = list(reversed(params.path))
        fees = list(reversed(params.fees))
        (
            amount_out,
            sqrt_price_limit_x96_after_list,
            initialized_ticks_crossed_list,
            gas_estimate,
        ) = self.contract.functions.quoteExactInput(
            encode_path(path, fees),
            params.amount_in,
        ).call()

        return QuoteExactInput(
            amount_out=amount_out,
            sqrt_price_limit_x96_after_list=sqrt_price_limit_x96_after_list,
            initialized_ticks_crossed_list=initialized_ticks_crossed_list,
            gas_estimate=gas_estimate,
        )

    def quote_exact_input_single(self, params: QuoteExactInputSingleParams) -> QuoteExactInputSingle:
        (
            amount_out,
            sqrt_price_limit_x96_after,
            initialized_ticks_crossed,
            gas_estimate,
        ) = self.contract.functions.quoteExactInputSingle(
            (
                params.token_in,
                params.token_out,
                params.amount_in,
                params.fee,
                params.sqrt_price_limit_x96,
            )
        ).call()

        return QuoteExactInputSingle(
            amount_out=amount_out,
            sqrt_price_limit_x96_after=sqrt_price_limit_x96_after,
            initialized_ticks_crossed=initialized_ticks_crossed,
            gas_estimate=gas_estimate,
        )
