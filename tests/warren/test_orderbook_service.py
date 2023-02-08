import pytest
from decimal import Decimal
from tokens.dai import DAI
from tokens.weth9 import WETH9
from warren.core.create_token_pair import create_token_pair
from warren.models.order import OrderDto, OrderStatus, OrderType
from warren.models.token_pair import TokenPair
from warren.services.order_book_service import OrderBookService
from warren.services.transaction_service import TransactionService
from warren.utils.to_wei import to_wei


@pytest.mark.asyncio
async def test_stop_losses(orderbook: OrderBookService, transaction_service: TransactionService):
    uniswap_v3_router_address = "0xE592427A0AEce92De3Edee1F18E0157C05861564"

    dai = DAI(web3=orderbook.web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F")
    weth9 = WETH9(web3=orderbook.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

    # current price = 1517024094830368309726
    trigger_price = to_wei(Decimal(1520.5), decimals=DAI.decimals())
    mock_order = OrderDto(
        type=OrderType.stop_loss,
        token0=weth9,
        token1=dai,
        trigger_price=int(trigger_price),
        percent=Decimal(1),
        status=OrderStatus.active,
    )
    orderbook.database.create_order(order=mock_order)

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

    await transaction_service.send_transaction(
        weth9.approve(
            uniswap_v3_router_address,
            max_amount_in=amount_in,
            gas_limit=fees.gas_limit,
            max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
            max_fee_per_gas=fees.max_fee_per_gas,
        )
    )

    assert weth9.balance_of(orderbook.web3.eth.default_account) == int(1000000000000000000)
    assert dai.balance_of(orderbook.web3.eth.default_account) == int(0)

    order_list = orderbook.database.list_orders(web3=orderbook.web3, status=OrderStatus.active)
    assert len(order_list) == 1

    await orderbook.seek_for_opportunities()

    order_list = orderbook.database.list_orders(web3=orderbook.web3, status=OrderStatus.executed)
    assert len(order_list) == 1

    assert weth9.balance_of(orderbook.web3.eth.default_account) == int(0)
    assert dai.balance_of(orderbook.web3.eth.default_account) == int(1517024094830368309726)


# @pytest.mark.asyncio
# async def test_take_profit(orderbook: OrderBookService):
#     # current price = 1517024094830368309726
#     trigger_price = to_wei(Decimal(1500.75666), decimals=DAI.decimals())
#     mock_order = OrderDto(
#         type=OrderType.take_profit,
#         token_pair=TokenPair.weth9_dai,
#         trigger_price=int(trigger_price),
#         percent=Decimal(1),
#         status=OrderStatus.active,
#     )
#     orderbook.database.create_order(order=mock_order)

#     weth9 = WETH9(web3=orderbook.web3, transaction_service=orderbook.transaction_service)
#     amount_in = int(1 * 10**18)
#     await weth9.deposit(amount_in=amount_in)
#     await weth9.approve(uniswap_v3_router_address, max_amount_in=amount_in)

#     uniswap_v3_weth9_dai_pair = create_token_pair(
#         async_web3=orderbook.async_web3,
#         web3=orderbook.web3,
#         transaction_service=orderbook.transaction_service,
#         token_pair=TokenPair.weth9_dai,
#     )

#     (weth9_balance, dai_balance) = uniswap_v3_weth9_dai_pair.balances()
#     assert weth9_balance == int(1000000000000000000)
#     assert dai_balance == int(0)

#     order_list = orderbook.database.list_orders(status=OrderStatus.active)
#     assert len(order_list) == 1

#     await orderbook.seek_for_opportunities()

#     order_list = orderbook.database.list_orders(status=OrderStatus.executed)
#     assert len(order_list) == 1

#     (weth9_balance, dai_balance) = uniswap_v3_weth9_dai_pair.balances()
#     assert weth9_balance == int(0)
#     assert dai_balance == int(1517024094830368309726)
