import pytest

from decimal import Decimal
from warren.core.uniswap_v3_weth9_dai_token_pair import UniswapV3WEth9DaiTokenPair
from warren.models.order import OrderDto, OrderStatus, OrderType
from warren.models.token_pair import TokenPair
from warren.services.order_book_service import OrderBookService
from warren.tokens.weth9 import WEth9
from warren.uniswap.v3.router import uniswap_v3_router_address

@pytest.mark.asyncio
async def test_stop_losses(orderbook: OrderBookService):
    # current price = 1517024094830368309726
    mock_order = OrderDto(
        type=OrderType.stop_loss,
        token_pair=TokenPair.weth9_dai,
        trigger_price=int(1600000000000000000000),
        percent=Decimal(1),
        status=OrderStatus.active,
    )
    orderbook.database.create_order(order=mock_order)

    weth9 = WEth9(web3=orderbook.web3, transaction_service=orderbook.transaction_service)
    amount_in = int(1 * 10**18)
    await weth9.deposit(amount_in=amount_in)
    await weth9.approve(
        uniswap_v3_router_address, max_amount_in=amount_in
    )

    uniswap_v3_weth9_dai_pair = UniswapV3WEth9DaiTokenPair(
        async_web3=orderbook.async_web3,
        web3=orderbook.web3,
        transaction_service=orderbook.transaction_service,
    )

    (weth9_balance, dai_balance) = uniswap_v3_weth9_dai_pair.balances()
    assert weth9_balance == int(1000000000000000000)
    assert dai_balance == int(0)

    order_list = orderbook.database.list_orders(status=OrderStatus.active)
    assert len(order_list) == 1

    await orderbook.seek_for_opportunities()

    order_list = orderbook.database.list_orders(status=OrderStatus.executed)
    assert len(order_list) == 1

    (weth9_balance, dai_balance) = uniswap_v3_weth9_dai_pair.balances()
    assert weth9_balance == int(0)
    assert dai_balance == int(1517024094830368309726)



@pytest.mark.asyncio
async def test_take_profit(orderbook: OrderBookService):
    # current price = 1517024094830368309726
    mock_order = OrderDto(
        type=OrderType.take_profit,
        token_pair=TokenPair.weth9_dai,
        trigger_price=int(1500000000000000000000),
        percent=Decimal(1),
        status=OrderStatus.active,
    )
    orderbook.database.create_order(order=mock_order)

    weth9 = WEth9(web3=orderbook.web3, transaction_service=orderbook.transaction_service)
    amount_in = int(1 * 10**18)
    await weth9.deposit(amount_in=amount_in)
    await weth9.approve(
        uniswap_v3_router_address, max_amount_in=amount_in
    )

    uniswap_v3_weth9_dai_pair = UniswapV3WEth9DaiTokenPair(
        async_web3=orderbook.async_web3,
        web3=orderbook.web3,
        transaction_service=orderbook.transaction_service,
    )

    (weth9_balance, dai_balance) = uniswap_v3_weth9_dai_pair.balances()
    assert weth9_balance == int(1000000000000000000)
    assert dai_balance == int(0)

    order_list = orderbook.database.list_orders(status=OrderStatus.active)
    assert len(order_list) == 1

    await orderbook.seek_for_opportunities()

    order_list = orderbook.database.list_orders(status=OrderStatus.executed)
    assert len(order_list) == 1

    (weth9_balance, dai_balance) = uniswap_v3_weth9_dai_pair.balances()
    assert weth9_balance == int(0)
    assert dai_balance == int(1517024094830368309726)