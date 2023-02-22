import pytest
from web3 import Web3
from tokens.dai import DAI
from tokens.weth9 import WETH9
from exchanges.uniswap.v2.factory import UniswapV2Factory
from exchanges.uniswap.v2.models.exact_tokens_for_tokens_params import ExactTokensForTokensParams
from exchanges.uniswap.v2.models.get_pair_params import GetPairParams
from exchanges.uniswap.v2.router import UniswapV2Router
from warren.managers.transaction_manager import TransactionManager


@pytest.mark.asyncio
async def test_uniswap_v2_router01(web3: Web3, transaction_service: TransactionManager):
    uniswap_v2_factory_address = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    uniswap_v2_factory = UniswapV2Factory(web3=web3, address=uniswap_v2_factory_address)

    dai = DAI(web3=web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F")
    weth9 = WETH9(web3=web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

    pair_params = GetPairParams(token0=weth9.address, token1=dai.address)
    uniswap_v2_pair = uniswap_v2_factory.get_pair(pair_params)

    amount_in = int(1 * 10**18)
    amount_out = uniswap_v2_pair.calculate_token0_to_token1_amount_out(amount_in=amount_in)
    assert amount_out == 1514276931280896357898

    uniswap_v2_router_address = "0xf164fC0Ec4E93095b804a4795bBe1e041497b92a"
    uniswap_v2_router = UniswapV2Router(web3=web3, address=uniswap_v2_router_address)

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
            uniswap_v2_router_address,
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
        uniswap_v2_router.swap_exact_tokens_for_tokens(params, fees.gas_limit, fees.max_fee_per_gas, fees.max_fee_per_gas)
    )

    assert weth9.balance_of(web3.eth.default_account) == int(0)
    assert dai.balance_of(web3.eth.default_account) == int(1514276931280896357898)


@pytest.mark.asyncio
async def test_uniswap_v2_router02(web3: Web3, transaction_service: TransactionManager):
    uniswap_v2_factory_address = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    uniswap_v2_factory = UniswapV2Factory(web3=web3, address=uniswap_v2_factory_address)

    dai = DAI(web3=web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F")
    weth9 = WETH9(web3=web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

    pair_params = GetPairParams(token0=weth9.address, token1=dai.address)
    uniswap_v2_pair = uniswap_v2_factory.get_pair(pair_params)

    amount_in = int(1 * 10**18)
    amount_out = uniswap_v2_pair.calculate_token0_to_token1_amount_out(amount_in=amount_in)
    assert amount_out == 1514276931280896357898

    uniswap_v2_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    uniswap_v2_router = UniswapV2Router(web3=web3, address=uniswap_v2_router_address)

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
            uniswap_v2_router_address,
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
        uniswap_v2_router.swap_exact_tokens_for_tokens(params, fees.gas_limit, fees.max_fee_per_gas, fees.max_fee_per_gas)
    )

    assert weth9.balance_of(web3.eth.default_account) == int(0)
    assert dai.balance_of(web3.eth.default_account) == int(1514276931280896357898)
