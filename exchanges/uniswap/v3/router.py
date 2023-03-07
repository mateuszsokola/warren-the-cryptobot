from web3 import Web3
from exchanges.uniswap.v3.models.exact_input_params import ExactInputParams

from exchanges.uniswap.v3.models.exact_input_single_params import ExactInputSingleParams
from exchanges.uniswap.v3.utils.encode_path import encode_path
from warren.utils.load_contract_abi import load_contract_abi

uniswap_v3_router_address = "0xE592427A0AEce92De3Edee1F18E0157C05861564"


class UniswapV3Router:
    def __init__(self, web3: Web3, address: str):
        self.web3 = web3

        self.address = address
        self.contract = web3.eth.contract(
            address=address,
            abi=load_contract_abi("ISwapRouter.json", "artifacts/uniswap/v3"),
        )

    def exact_input(
        self,
        params: ExactInputParams,
        gas_limit: int,
        max_priority_fee_per_gas: int,
        max_fee_per_gas: int,
    ):
        path = list(reversed(params.path))
        fees = list(reversed(params.fees))

        tx = self.contract.functions.exactInput(
            [
                encode_path(path, fees),
                params.recipient,
                params.deadline,
                params.amount_in,
                params.min_amount_out,
            ]
        ).build_transaction(
            {
                "type": 2,
                "gas": gas_limit,
                "maxPriorityFeePerGas": max_priority_fee_per_gas,
                "maxFeePerGas": max_fee_per_gas,
            }
        )

        return tx

    def exact_input_single(
        self,
        params: ExactInputSingleParams,
        gas_limit: int,
        max_priority_fee_per_gas: int,
        max_fee_per_gas: int,
    ):
        tx = self.contract.functions.exactInputSingle(
            [
                params.token_in,
                params.token_out,
                params.fee,
                params.recipient,
                params.deadline,
                params.amount_in,
                params.amount_out_minimum,
                params.sqrt_price_limit_x96,
            ]
        ).build_transaction(
            {
                "type": 2,
                "gas": gas_limit,
                "maxPriorityFeePerGas": max_priority_fee_per_gas,
                "maxFeePerGas": max_fee_per_gas,
            }
        )

        return tx
