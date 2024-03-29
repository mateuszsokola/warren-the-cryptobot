import pytest
from web3 import Web3
from exchanges.uniswap.v3.models.exact_input_params import ExactInputParams
from tokens.base_token import BaseToken
from tokens.dai import DAI
from tokens.weth9 import WETH9
from exchanges.uniswap.v3.models.exact_input_single_params import ExactInputSingleParams
from exchanges.uniswap.v3.models.quote_exact_input_single_params import QuoteExactInputSingleParams
from exchanges.uniswap.v3.pool import UniswapV3Pool
from exchanges.uniswap.v3.quoter_v2 import UniswapV3QuoterV2
from exchanges.uniswap.v3.router import UniswapV3Router
from warren.managers.transaction_manager import TransactionManager


@pytest.mark.asyncio
async def test_uniswap_v3_exact_input_single(web3: Web3, transaction_service: TransactionManager):
    uniswap_v3_router_address = "0xE592427A0AEce92De3Edee1F18E0157C05861564"

    uniswap_v3_pool = UniswapV3Pool(web3=web3, address="0xC2e9F25Be6257c210d7Adf0D4Cd6E3E881ba25f8")
    uniswap_v3_router = UniswapV3Router(web3=web3, address=uniswap_v3_router_address)
    uniswap_v3_quoter = UniswapV3QuoterV2(web3=web3, address="0x61fFE014bA17989E743c5F6cB21bF9697530B21e")

    link = BaseToken(web3=web3, address="0x514910771AF9Ca656af840dff83E8264EcF986CA", name="LINK")
    dai = DAI(web3=web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F")
    weth9 = WETH9(web3=web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

    amount_in = int(1 * 10**18)

    params = QuoteExactInputSingleParams(
        token_in=weth9.address, token_out=dai.address, fee=uniswap_v3_pool.fee(), amount_in=amount_in, sqrt_price_limit_x96=0
    )
    quotation = uniswap_v3_quoter.quote_exact_input_single(params)
    assert quotation.amount_out == 1517024094830368309726

    fees = await transaction_service.calculate_tx_fees(gas_limit=500000)

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
            uniswap_v3_router_address,
            max_amount_in=amount_in,
            gas_limit=fees.gas_limit,
            max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
            max_fee_per_gas=fees.max_fee_per_gas,
        )
    )

    params = ExactInputSingleParams(
        token_in=weth9.address,
        token_out=dai.address,
        fee=uniswap_v3_pool.fee(),
        amount_in=amount_in,
        amount_out_minimum=0,
        recipient=web3.eth.default_account,
        deadline=99999999999999,
        sqrt_price_limit_x96=0,
    )
    await transaction_service.send_transaction(
        uniswap_v3_router.exact_input_single(params, fees.gas_limit, fees.max_fee_per_gas, fees.max_fee_per_gas)
    )

    assert weth9.balance_of(web3.eth.default_account) == int(0)
    assert dai.balance_of(web3.eth.default_account) == int(1517024094830368309726)

    await transaction_service.send_transaction(
        dai.approve(
            uniswap_v3_router_address,
            max_amount_in=1517024094830368309726,
            gas_limit=fees.gas_limit,
            max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
            max_fee_per_gas=fees.max_fee_per_gas,
        )
    )

    path = [
        "0x514910771AF9Ca656af840dff83E8264EcF986CA",  # LINK
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH9
        "0x6B175474E89094C44Da98b954EedeAC495271d0F",  # DAI
    ]

    params = ExactInputParams(
        path=path,
        fees=[3000, 3000],
        amount_in=1517024094830368309726,
        min_amount_out=0,
        recipient=web3.eth.default_account,
        deadline=99999999999999,
    )
    await transaction_service.send_transaction(
        uniswap_v3_router.exact_input(params, fees.gas_limit, fees.max_fee_per_gas, fees.max_fee_per_gas)
    )
    assert link.balance_of(web3.eth.default_account) == int(223156778094723040368)


@pytest.mark.asyncio
async def test_uniswap_v3_exact_input_single(web3: Web3, transaction_service: TransactionManager):
    uniswap_v3_router_address = "0xE592427A0AEce92De3Edee1F18E0157C05861564"

    uniswap_v3_pool = UniswapV3Pool(web3=web3, address="0xC2e9F25Be6257c210d7Adf0D4Cd6E3E881ba25f8")
    uniswap_v3_router = UniswapV3Router(web3=web3, address=uniswap_v3_router_address)
    uniswap_v3_quoter = UniswapV3QuoterV2(web3=web3, address="0x61fFE014bA17989E743c5F6cB21bF9697530B21e")

    dai = DAI(web3=web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F")
    weth9 = WETH9(web3=web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

    amount_in = int(1 * 10**18)

    params = QuoteExactInputSingleParams(
        token_in=weth9.address, token_out=dai.address, fee=uniswap_v3_pool.fee(), amount_in=amount_in, sqrt_price_limit_x96=0
    )
    quotation = uniswap_v3_quoter.quote_exact_input_single(params)
    assert quotation.amount_out == 1517024094830368309726

    fees = await transaction_service.calculate_tx_fees(gas_limit=200000)

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
            uniswap_v3_router_address,
            max_amount_in=amount_in,
            gas_limit=fees.gas_limit,
            max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
            max_fee_per_gas=fees.max_fee_per_gas,
        )
    )

    params = ExactInputSingleParams(
        token_in=weth9.address,
        token_out=dai.address,
        fee=uniswap_v3_pool.fee(),
        amount_in=amount_in,
        amount_out_minimum=0,
        recipient=web3.eth.default_account,
        deadline=99999999999999,
        sqrt_price_limit_x96=0,
    )
    await transaction_service.send_transaction(
        uniswap_v3_router.exact_input_single(params, fees.gas_limit, fees.max_fee_per_gas, fees.max_fee_per_gas)
    )

    assert weth9.balance_of(web3.eth.default_account) == int(0)
    assert dai.balance_of(web3.eth.default_account) == int(1517024094830368309726)
