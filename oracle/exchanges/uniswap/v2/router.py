from web3 import Web3
from oracle.exchanges.uniswap.v2.models.exact_eth_for_tokens_params import ExactETHForTokensParams
from oracle.exchanges.uniswap.v2.models.exact_tokens_for_tokens_params import ExactTokensForTokensParams
from oracle.utils.load_contract_abi import load_contract_abi


class UniswapV2Router:
    def __init__(self, web3: Web3, address: str):
        self.web3 = web3

        self.address = address
        self.contract = web3.eth.contract(
            address=address,
            abi=load_contract_abi("IUniswapV2Router02.json"),
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

    def swap_exact_ETH_for_tokens(
        self,
        params: ExactETHForTokensParams,
        gas_limit: int,
        max_priority_fee_per_gas: int,
        max_fee_per_gas: int,
    ):
        tx = self.contract.functions.swapExactETHForTokens(
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
                "value": params.amount_in,
            }
        )

        return tx
