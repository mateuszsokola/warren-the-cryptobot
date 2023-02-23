from web3 import Web3
from exchanges.stableswap.models.exchange_params import ExchangeParams
from exchanges.stableswap.models.get_dy_params import GetDyParams

from warren.utils.load_contract_abi import load_contract_abi


class StableSwap3pool:
    def __init__(self, web3: Web3, address: str):
        self.web3 = web3

        self.address = address
        self.contract = web3.eth.contract(
            address=address,
            abi=load_contract_abi("IStableSwap3Pool.json", "artifacts/stableswap"),
        )

    # Note: In the EURS Pool, the decimals for coins(0) and coins(1) are 2 and 18, respectively.
    def get_dy(
        self,
        params: GetDyParams,
    ) -> int:
        amount_out = self.contract.functions.get_dy(
            params.token0_index,
            params.token1_index,
            params.amount_in,
        ).call()

        return amount_out

    def fee(self) -> int:
        fee = self.contract.functions.fee().call()

        return fee

    def exchange(
        self,
        params: ExchangeParams,
        gas_limit: int,
        max_priority_fee_per_gas: int,
        max_fee_per_gas: int,
    ):
        tx = self.contract.functions.exchange(
            params.token0_index,
            params.token1_index,
            params.amount_in,
            params.min_amount_out,
        ).build_transaction(
            {
                "type": 2,
                "gas": gas_limit,
                "maxPriorityFeePerGas": max_priority_fee_per_gas,
                "maxFeePerGas": max_fee_per_gas,
            }
        )

        return tx
