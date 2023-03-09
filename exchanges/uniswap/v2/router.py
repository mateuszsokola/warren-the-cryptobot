from web3 import Web3
from exchanges.uniswap.v2.models.exact_tokens_for_tokens_params import ExactTokensForTokensParams
from warren.utils.load_contract_abi import load_contract_abi


class UniswapV2Router:
    def __init__(self, web3: Web3, address: str):
        self.web3 = web3

        self.address = address
        self.contract = web3.eth.contract(
            address=address,
            abi=load_contract_abi("Router.json", "artifacts/uniswap/v2"),
        )

    def swap_exact_tokens_for_tokens(
        self,
        params: ExactTokensForTokensParams,
        gas_limit: int,
        max_priority_fee_per_gas: int,
        max_fee_per_gas: int,
    ):
        tx = self.contract.functions.swapExactTokensForTokens(
            params.amount_in,
            params.amount_out_minimum,
            params.path,
            params.recipient,
            params.deadline,
        ).build_transaction(
            {
                "type": 2,
                "gas": gas_limit,
                "maxPriorityFeePerGas": max_priority_fee_per_gas,
                "maxFeePerGas": max_fee_per_gas,
            }
        )

        return tx
