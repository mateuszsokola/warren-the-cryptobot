import pytest
from web3 import Web3
from tokens.weth9 import WETH9
from warren.services.transaction_service import TransactionService


@pytest.mark.asyncio
async def test_eth_to_weth9(web3: Web3, transaction_service: TransactionService):
    weth9 = WETH9(web3=web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

    assert weth9.balance_of(web3.eth.default_account) == int(0)

    fees = await transaction_service.calculate_tx_fees()
    amount_in = int(1 * 10**18)

    await transaction_service.send_transaction(
        weth9.deposit(
            amount_in=amount_in,
            gas_limit=fees.gas_limit,
            max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
            max_fee_per_gas=fees.max_fee_per_gas,
        )
    )

    assert weth9.balance_of(web3.eth.default_account) == int(amount_in)
