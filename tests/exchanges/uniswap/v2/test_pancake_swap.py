from fractions import Fraction
import pytest
from web3 import Web3
from tokens.usdc import USDC
from tokens.weth9 import WETH9
from exchanges.uniswap.v2.factory import UniswapV2Factory
from exchanges.uniswap.v2.models.exact_tokens_for_tokens_params import ExactTokensForTokensParams
from exchanges.uniswap.v2.models.get_pair_params import GetPairParams
from exchanges.uniswap.v2.router import UniswapV2Router
from warren.services.transaction_service import TransactionService


@pytest.mark.asyncio
async def test_pancake_swap(web3: Web3, transaction_service: TransactionService):
    pancake_factory_address = "0x1097053Fd2ea711dad45caCcc45EfF7548fCB362"
    pancake_factory = UniswapV2Factory(web3=web3, address=pancake_factory_address)

    usdc = USDC(web3=web3, address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    weth9 = WETH9(web3=web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

    pair_params = GetPairParams(token0=weth9.address, token1=usdc.address)
    uniswap_v2_pair = pancake_factory.get_pair(pair_params, fee=Fraction(25, 10000))

    amount_in = int(1 * 10**18)
    amount_out = uniswap_v2_pair.calculate_token0_to_token1_amount_out(amount_in=amount_in)
    assert amount_out == 1516644656

    pancake_router_address = "0xEfF92A263d31888d860bD50809A8D171709b7b1c"
    pancake_router = UniswapV2Router(web3=web3, address=pancake_router_address)

    fees = await transaction_service.calculate_tx_fees()

    await transaction_service.send_transaction(
        weth9.deposit(
            amount_in=amount_in,
            gas_limit=fees.gas_limit,
            max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
            max_fee_per_gas=fees.max_fee_per_gas,
        )
    )

    await transaction_service.send_transaction(
        weth9.approve(
            pancake_router_address,
            max_amount_in=amount_in,
            gas_limit=fees.gas_limit,
            max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
            max_fee_per_gas=fees.max_fee_per_gas,
        )
    )

    params = ExactTokensForTokensParams(
        token_in=weth9.address,
        token_out=usdc.address,
        amount_in=amount_in,
        amount_out_minimum=0,
        deadline=9999999999999999,
    )
    await transaction_service.send_transaction(
        pancake_router.swap_exact_tokens_for_tokens(params, fees.gas_limit, fees.max_fee_per_gas, fees.max_fee_per_gas)
    )

    assert weth9.balance_of(web3.eth.default_account) == int(0)
    assert usdc.balance_of(web3.eth.default_account) == int(1516644656)
