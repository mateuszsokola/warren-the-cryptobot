from web3 import Web3

from warren.uniswap.v3.models.quote_exact_input_single_params import (
    QuoteExactInputSingleParams,
)
from warren.utils.load_contract_abi import load_contract_abi

uniswap_v3_quoter_address = "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6"


class UniswapV3Quoter:
    def __init__(self, web3: Web3):
        self.web3 = web3
        self.address = uniswap_v3_quoter_address
        self.contract = web3.eth.contract(
            address=uniswap_v3_quoter_address,
            abi=load_contract_abi("IQuoter.json", "artifacts/uniswap/v3"),
        )

    def quote_exact_input_single(self, params: QuoteExactInputSingleParams) -> int:
        amount = self.contract.functions.quoteExactInputSingle(
            params.token_in,
            params.token_out,
            params.fee,
            params.amount_in,
            params.sqrt_price_limit_x96,
        ).call()

        return int(amount)
