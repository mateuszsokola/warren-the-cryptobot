import pytest

from warren.services.order_book_service import OrderBookService
from tokens.dai import DAI
from tokens.weth9 import WETH9
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
