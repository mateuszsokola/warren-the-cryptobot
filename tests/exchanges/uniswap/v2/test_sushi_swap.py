import pytest
from web3 import Web3
from tokens.dai import DAI
from tokens.weth9 import WETH9
from exchanges.uniswap.v2.factory import UniswapV2Factory
from exchanges.uniswap.v2.models.exact_tokens_for_tokens_params import ExactTokensForTokensParams
from exchanges.uniswap.v2.models.get_pair_params import GetPairParams
from exchanges.uniswap.v2.router import UniswapV2Router
from warren.services.transaction_service import TransactionService


@pytest.mark.asyncio
async def test_sushi_swap(web3: Web3, transaction_service: TransactionService):
    sushi_factory_address = "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"
    sushi_factory = UniswapV2Factory(web3=web3, address=sushi_factory_address)

    dai = DAI(web3=web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F")
    weth9 = WETH9(web3=web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

    pair_params = GetPairParams(token0=weth9.address, token1=dai.address)
    sushi_pair = sushi_factory.get_pair(pair_params)

    amount_in = int(1 * 10**18)
    amount_out = sushi_pair.calculate_token0_to_token1_amount_out(amount_in=amount_in)
    assert amount_out == 1513624364509613607658

    sushi_router_address = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    sushi_router = UniswapV2Router(web3=web3, address=sushi_router_address)

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
            sushi_router_address,
            max_amount_in=amount_in,
            gas_limit=fees.gas_limit,
            max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
            max_fee_per_gas=fees.max_fee_per_gas,
        )
    )

    params = ExactTokensForTokensParams(
        token_in=weth9.address,
        token_out=dai.address,
        amount_in=amount_in,
        amount_out_minimum=0,
        deadline=9999999999999999,
    )
    await transaction_service.send_transaction(
        sushi_router.swap_exact_tokens_for_tokens(params, fees.gas_limit, fees.max_fee_per_gas, fees.max_fee_per_gas)
    )

    assert weth9.balance_of(web3.eth.default_account) == int(0)
    assert dai.balance_of(web3.eth.default_account) == int(1513624364509613607658)
