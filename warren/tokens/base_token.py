from web3 import Web3
from warren.services.transaction_service import TransactionService
from warren.utils.load_contract_abi import load_contract_abi


class BaseToken:
    def __init__(
        self,
        web3: Web3,
        transaction_service: TransactionService,
        address: str,
        name: str,
        abi_name: str = "IERC20.json",
    ):
        self.web3 = web3
        self.transaction_service = transaction_service
        self.name = name
        self.address = address
        self.contract = web3.eth.contract(address=address, abi=load_contract_abi(abi_name, "artifacts/tokens"))

    async def approve(self, address: str, max_amount_in: int, gas: int = 120000):
        max_tx_fees = await self.transaction_service.calculate_tx_fees()
        tx = self.contract.functions.approve(address, max_amount_in).build_transaction(
            {
                "type": 2,
                "gas": gas,
                "maxPriorityFeePerGas": max_tx_fees.max_priority_fee_per_gas,
                "maxFeePerGas": max_tx_fees.max_fee_per_gas,
            }
        )

        tx_hash = await self.transaction_service.send_transaction(tx)

        return tx_hash

    def balance_of(self, address: str):
        return self.contract.functions.balanceOf(address).call()

    @staticmethod
    def decimals() -> int:
        return 18
