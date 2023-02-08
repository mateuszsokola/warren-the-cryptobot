from web3 import Web3
from tokens.base_token import BaseToken


class WETH9(BaseToken):
    def __init__(self, web3: Web3, address: str) -> None:
        super().__init__(
            web3=web3,
            address=address,
            name="WETH9",
            abi_name="WETH9.json",
        )

    def deposit(self, amount_in: int, gas_limit: int, max_priority_fee_per_gas: int, max_fee_per_gas: int):
        tx = self.contract.functions.deposit().build_transaction(
            {
                "type": 2,
                "gas": gas_limit,
                "maxPriorityFeePerGas": max_priority_fee_per_gas,
                "maxFeePerGas": max_fee_per_gas,
                "value": amount_in,
            }
        )

        return tx
