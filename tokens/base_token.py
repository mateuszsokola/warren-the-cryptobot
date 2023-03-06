from web3 import Web3
from warren.utils.load_contract_abi import load_contract_abi


class BaseToken:
    decimals: int = 18

    def __init__(
        self,
        web3: Web3,
        address: str,
        name: str,
        abi_name: str = "IERC20.json",
        decimals: int = 18,
        native: bool = False,
    ):
        self.web3 = web3
        self.name = name
        self.address = address
        self.contract = (
            None
            if native == True
            else web3.eth.contract(
                address=address,
                abi=load_contract_abi(abi_name, "artifacts/tokens"),
            )
        )
        self.decimals = decimals
        self.native = native

    def approve(
        self,
        address: str,
        max_amount_in: int,
        gas_limit: int,
        max_priority_fee_per_gas: int,
        max_fee_per_gas: int,
    ):
        tx = self.contract.functions.approve(address, max_amount_in).build_transaction(
            {
                "type": 2,
                "gas": gas_limit,
                "maxPriorityFeePerGas": max_priority_fee_per_gas,
                "maxFeePerGas": max_fee_per_gas,
            }
        )

        return tx

    def balance_of(self, address: str):
        return self.contract.functions.balanceOf(address).call()
