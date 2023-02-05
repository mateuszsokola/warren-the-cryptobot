import pytest
from fractions import Fraction

from warren.services.order_book_service import OrderBookService
from warren.tokens.dai import Dai, dai_contract_address
from warren.tokens.usdc import UsdC, usdc_contract_address
from warren.tokens.weth9 import WEth9, weth9_contract_address
from exchanges.uniswap.v2.factory import UniswapV2Factory
from exchanges.uniswap.v2.models.exact_tokens_for_tokens_params import ExactTokensForTokensParams
from exchanges.uniswap.v2.models.get_pair_params import GetPairParams
from exchanges.uniswap.v2.router import UniswapV2Router


@pytest.mark.asyncio
async def test_uniswap_v2_router01(orderbook: OrderBookService):
    uniswap_v2_factory_address = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    uniswap_v2_factory = UniswapV2Factory(
        web3=orderbook.web3, transaction_service=orderbook.transaction_service, address=uniswap_v2_factory_address
    )

    pair_params = GetPairParams(token_in=weth9_contract_address, token_out=dai_contract_address)
    uniswap_v2_pair = uniswap_v2_factory.get_pair(pair_params)

    amount_in = int(1 * 10**18)
    amount_out = uniswap_v2_pair.calculate_token0_to_token1_amount_out(amount_in=amount_in)
    assert amount_out == 1514276931280896357898

    uniswap_v2_router_address = "0xf164fC0Ec4E93095b804a4795bBe1e041497b92a"
    uniswap_v2_router = UniswapV2Router(
        web3=orderbook.web3, transaction_service=orderbook.transaction_service, address=uniswap_v2_router_address
    )

    dai = Dai(web3=orderbook.web3, transaction_service=orderbook.transaction_service)
    weth9 = WEth9(web3=orderbook.web3, transaction_service=orderbook.transaction_service)
    await weth9.deposit(amount_in=amount_in)
    await weth9.approve(uniswap_v2_router_address, max_amount_in=amount_in)

    fee = await orderbook.transaction_service.calculate_tx_fees()

    params = ExactTokensForTokensParams(
        token_in=weth9_contract_address,
        token_out=dai_contract_address,
        amount_in=amount_in,
        amount_out_minimum=0,
        deadline=9999999999999999,
    )
    tx_params = uniswap_v2_router.swap_exact_tokens_for_tokens(params, fee.gas_limit, fee.max_fee_per_gas, fee.max_fee_per_gas)
    await orderbook.transaction_service.send_transaction(tx_params)

    assert weth9.balance_of(orderbook.web3.eth.default_account) == int(0)
    assert dai.balance_of(orderbook.web3.eth.default_account) == int(1514276931280896357898)


@pytest.mark.asyncio
async def test_uniswap_v2_router02(orderbook: OrderBookService):
    uniswap_v2_factory_address = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    uniswap_v2_factory = UniswapV2Factory(
        web3=orderbook.web3, transaction_service=orderbook.transaction_service, address=uniswap_v2_factory_address
    )

    pair_params = GetPairParams(token_in=weth9_contract_address, token_out=dai_contract_address)
    uniswap_v2_pair = uniswap_v2_factory.get_pair(pair_params)

    amount_in = int(1 * 10**18)
    amount_out = uniswap_v2_pair.calculate_token0_to_token1_amount_out(amount_in=amount_in)
    assert amount_out == 1514276931280896357898

    uniswap_v2_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    uniswap_v2_router = UniswapV2Router(
        web3=orderbook.web3, transaction_service=orderbook.transaction_service, address=uniswap_v2_router_address
    )

    dai = Dai(web3=orderbook.web3, transaction_service=orderbook.transaction_service)
    weth9 = WEth9(web3=orderbook.web3, transaction_service=orderbook.transaction_service)
    await weth9.deposit(amount_in=amount_in)
    await weth9.approve(uniswap_v2_router_address, max_amount_in=amount_in)

    fee = await orderbook.transaction_service.calculate_tx_fees()

    params = ExactTokensForTokensParams(
        token_in=weth9_contract_address,
        token_out=dai_contract_address,
        amount_in=amount_in,
        amount_out_minimum=0,
        deadline=9999999999999999,
    )
    tx_params = uniswap_v2_router.swap_exact_tokens_for_tokens(params, fee.gas_limit, fee.max_fee_per_gas, fee.max_fee_per_gas)
    await orderbook.transaction_service.send_transaction(tx_params)

    assert weth9.balance_of(orderbook.web3.eth.default_account) == int(0)
    assert dai.balance_of(orderbook.web3.eth.default_account) == int(1514276931280896357898)


@pytest.mark.asyncio
async def test_sushiswap(orderbook: OrderBookService):
    sushiswap_factory_address = "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"
    sushiswap_factory = UniswapV2Factory(
        web3=orderbook.web3, transaction_service=orderbook.transaction_service, address=sushiswap_factory_address
    )

    pair_params = GetPairParams(token_in=weth9_contract_address, token_out=dai_contract_address)
    uniswap_v2_pair = sushiswap_factory.get_pair(pair_params)

    amount_in = int(1 * 10**18)
    amount_out = uniswap_v2_pair.calculate_token0_to_token1_amount_out(amount_in=amount_in)
    assert amount_out == 1513624364509613607658

    sushiswap_router_address = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    uniswap_v2_router = UniswapV2Router(
        web3=orderbook.web3, transaction_service=orderbook.transaction_service, address=sushiswap_router_address
    )

    dai = Dai(web3=orderbook.web3, transaction_service=orderbook.transaction_service)
    weth9 = WEth9(web3=orderbook.web3, transaction_service=orderbook.transaction_service)
    await weth9.deposit(amount_in=amount_in)
    await weth9.approve(sushiswap_router_address, max_amount_in=amount_in)

    fee = await orderbook.transaction_service.calculate_tx_fees()

    params = ExactTokensForTokensParams(
        token_in=weth9_contract_address,
        token_out=dai_contract_address,
        amount_in=amount_in,
        amount_out_minimum=0,
        deadline=9999999999999999,
    )
    tx_params = uniswap_v2_router.swap_exact_tokens_for_tokens(params, fee.gas_limit, fee.max_fee_per_gas, fee.max_fee_per_gas)
    await orderbook.transaction_service.send_transaction(tx_params)

    assert weth9.balance_of(orderbook.web3.eth.default_account) == int(0)
    assert dai.balance_of(orderbook.web3.eth.default_account) == int(1513624364509613607658)


@pytest.mark.asyncio
async def test_pancakeswap(orderbook: OrderBookService):
    pancakeswap_factory_address = "0x1097053Fd2ea711dad45caCcc45EfF7548fCB362"
    pancakeswap_factory = UniswapV2Factory(
        web3=orderbook.web3, transaction_service=orderbook.transaction_service, address=pancakeswap_factory_address
    )

    pair_params = GetPairParams(token_in=weth9_contract_address, token_out=usdc_contract_address)
    uniswap_v2_pair = pancakeswap_factory.get_pair(pair_params, fee=Fraction(25, 10000))

    amount_in = int(1 * 10**18)
    amount_out = uniswap_v2_pair.calculate_token0_to_token1_amount_out(amount_in=amount_in)
    assert amount_out == 1516644656

    pancakeswap_router_address = "0xEfF92A263d31888d860bD50809A8D171709b7b1c"
    uniswap_v2_router = UniswapV2Router(
        web3=orderbook.web3, transaction_service=orderbook.transaction_service, address=pancakeswap_router_address
    )

    usdc = UsdC(web3=orderbook.web3, transaction_service=orderbook.transaction_service)
    weth9 = WEth9(web3=orderbook.web3, transaction_service=orderbook.transaction_service)
    await weth9.deposit(amount_in=amount_in)
    await weth9.approve(pancakeswap_router_address, max_amount_in=amount_in)

    fee = await orderbook.transaction_service.calculate_tx_fees()

    params = ExactTokensForTokensParams(
        token_in=weth9_contract_address,
        token_out=usdc_contract_address,
        amount_in=amount_in,
        amount_out_minimum=0,
        deadline=9999999999999999,
    )
    tx_params = uniswap_v2_router.swap_exact_tokens_for_tokens(params, fee.gas_limit, fee.max_fee_per_gas, fee.max_fee_per_gas)
    await orderbook.transaction_service.send_transaction(tx_params)

    assert weth9.balance_of(orderbook.web3.eth.default_account) == int(0)
    assert usdc.balance_of(orderbook.web3.eth.default_account) == int(1516644656)
