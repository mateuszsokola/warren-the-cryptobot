from web3 import Web3
from exchanges.mooniswap.models.swap_params import SwapParams
from exchanges.mooniswap.models.get_return_params import GetReturnParams

from warren.utils.load_contract_abi import load_contract_abi


class MooniSwap:
    def __init__(self, web3: Web3, address: str):
        self.web3 = web3

        self.address = address
        self.contract = web3.eth.contract(
            address=address,
            abi=load_contract_abi("IMooniswap.json", "artifacts/mooniswap"),
        )

    def get_return(
        self,
        params: GetReturnParams,
    ) -> int:
        amount_out = self.contract.functions.getReturn(
            params.token0,
            params.token1,
            params.amount_in,
        ).call()

        return amount_out

    def swap(
        self,
        params: SwapParams,
        gas_limit: int,
        max_priority_fee_per_gas: int,
        max_fee_per_gas: int,
    ):
        tx = self.contract.functions.swap(
            params.token0,
            params.token1,
            params.amount_in,
            params.min_amount_out,
            params.referrer,
        ).build_transaction(
            {
                "type": 2,
                "gas": gas_limit,
                "maxPriorityFeePerGas": max_priority_fee_per_gas,
                "maxFeePerGas": max_fee_per_gas,
            }
        )

        return tx
