from web3 import Web3
from warren.services.transaction_service import TransactionService
from warren.tokens.base_token import BaseToken

weth9_contract_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"


class WEth9(BaseToken):
    def __init__(self, web3: Web3, transaction_service: TransactionService) -> None:
        super().__init__(
            web3=web3,
            transaction_service=transaction_service,
            address=weth9_contract_address,
            name="WETH9",
            abi_name="WETH9.json",
        )

    async def deposit(self, amount_in: int, gas_limit: int = 120000):
        tx_fees = await self.transaction_service.calculate_tx_fees(gas_limit=120000)
        tx = self.contract.functions.deposit().build_transaction(
            {
                "type": 2,
                "gas": gas_limit,
                "maxPriorityFeePerGas": tx_fees.max_priority_fee_per_gas,
                "maxFeePerGas": tx_fees.max_fee_per_gas,
                "value": amount_in
            }
        )

        tx_hash = await self.transaction_service.send_transaction(tx)

        return tx_hash
