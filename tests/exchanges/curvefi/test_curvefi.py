import pytest
from web3 import Web3
from exchanges.curvefi.models.exchange_multiple import ExchangeMultiple
from exchanges.curvefi.models.get_exchange_multiple_amount_params import GetExchangeMultipleAmountParams
from exchanges.curvefi.registry_exchange import CurveRegistryExchange
from tokens.dai import DAI
from tokens.weth9 import WETH9
from exchanges.uniswap.v2.factory import UniswapV2Factory
from exchanges.uniswap.v2.models.exact_tokens_for_tokens_params import ExactTokensForTokensParams
from exchanges.uniswap.v2.models.get_pair_params import GetPairParams
from exchanges.uniswap.v2.router import UniswapV2Router
from warren.managers.transaction_manager import TransactionManager


# TODO(mateu.sh): extract to conftest.py (duplicated in every test case)
async def convert_eth_to_dai(web3: Web3, transaction_service: TransactionManager):
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
async def test_curvefi(web3: Web3, transaction_service: TransactionManager):
    await convert_eth_to_dai(web3, transaction_service)

    curvefi_address = "0x99a58482BD75cbab83b27EC03CA68fF489b5788f"
    curvefi = CurveRegistryExchange(web3=web3, address=curvefi_address)

    dai = DAI(web3=web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F")
    weth9 = WETH9(web3=web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

    amount_in = int(1514276931280896357898)
    assert dai.balance_of(web3.eth.default_account) == amount_in

    fees = await transaction_service.calculate_tx_fees(600000)

    await transaction_service.send_transaction(
        dai.approve(
            curvefi_address,
            max_amount_in=amount_in,
            gas_limit=fees.gas_limit,
            max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
            max_fee_per_gas=fees.max_fee_per_gas,
        )
    )

    params = GetExchangeMultipleAmountParams(
        route=[
            "0x6B175474E89094C44Da98b954EedeAC495271d0F",  # DAI
            "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",  # Curve.fi: DAI/USDC/USDT Pool
            "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT
            "0xD51a44d3FaE010294C616388b506AcdA1bfAAE46",  # Curve.fi: USDT/WBTC/WETH Pool
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH9
            "0x0000000000000000000000000000000000000000",
            "0x0000000000000000000000000000000000000000",
            "0x0000000000000000000000000000000000000000",
            "0x0000000000000000000000000000000000000000",
        ],
        swap_params=[
            [0, 2, 1],
            [0, 2, 3],
            [0, 0, 0],
            [0, 0, 0],
        ],
        amount_in=amount_in,
    )

    min_amount_out = curvefi.get_exchange_multiple_amount(params)
    assert min_amount_out == 993918543675242099

    params = ExchangeMultiple(
        route=[
            "0x6B175474E89094C44Da98b954EedeAC495271d0F",  # DAI
            "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",  # Curve.fi: DAI/USDC/USDT Pool
            "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT
            "0xD51a44d3FaE010294C616388b506AcdA1bfAAE46",  # Curve.fi: USDT/WBTC/WETH Pool
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH9
            "0x0000000000000000000000000000000000000000",
            "0x0000000000000000000000000000000000000000",
            "0x0000000000000000000000000000000000000000",
            "0x0000000000000000000000000000000000000000",
        ],
        swap_params=[
            [0, 2, 1],
            [0, 2, 3],
            [0, 0, 0],
            [0, 0, 0],
        ],
        amount_in=amount_in,
        min_amount_out=0,
    )

    await transaction_service.send_transaction(
        curvefi.exchange_multiple(
            params,
            fees.gas_limit,
            fees.max_fee_per_gas,
            fees.max_fee_per_gas,
        )
    )

    assert dai.balance_of(web3.eth.default_account) == int(0)
    # assert web3.eth.get_balance(web3.eth.default_account) == int(1)
    assert weth9.balance_of(web3.eth.default_account) == min_amount_out
