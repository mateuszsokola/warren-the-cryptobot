import pytest
from decimal import Decimal
from order_book.models.order_dto import OrderDto
from order_book.models.order_status import OrderStatus
from order_book.models.order_type import OrderType
from tokens.dai import DAI
from tokens.weth9 import WETH9
from order_book.core.order_book_service import OrderBookService
from warren.managers.transaction_manager import TransactionManager
from warren.utils.to_wei import to_wei


@pytest.mark.asyncio
async def test_stop_losses(orderbook: OrderBookService, transaction_service: TransactionManager):
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

    # TODO(mateu.sh): This route is actually wrong. Uniswap V2 is less expensive than v3 in this case
    # * Current price on uniswap_v3_quoter_v2: 1517.024094830368309726 DAI
    # * Current price on uniswap_v2_router02: 1473.276814248781148190 DAI
    # * Current price on sushiswap: 1472.650060106236758540 DAI
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

    order_list = orderbook.database.list_orders(status=OrderStatus.active)
    assert len(order_list) == 1

    await orderbook.find_opportunities()

    order_list = orderbook.database.list_orders(status=OrderStatus.executed)
    assert len(order_list) == 1

    assert weth9.balance_of(orderbook.web3.eth.default_account) == int(0)
    assert dai.balance_of(orderbook.web3.eth.default_account) == int(1517024094830368309726)


@pytest.mark.asyncio
async def test_take_profit(orderbook: OrderBookService, transaction_service: TransactionManager):
    uniswap_v3_router_address = "0xE592427A0AEce92De3Edee1F18E0157C05861564"

    dai = DAI(web3=orderbook.web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F")
    weth9 = WETH9(web3=orderbook.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

    # current price = 1517024094830368309726
    trigger_price = to_wei(Decimal(1500.75666), decimals=DAI.decimals())
    mock_order = OrderDto(
        type=OrderType.take_profit,
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

    # TODO(mateu.sh): This route is actually wrong. Uniswap V2 is less expensive than v3 in this case
    # * Current price on uniswap_v3_quoter_v2: 1517.024094830368309726 DAI
    # * Current price on uniswap_v2_router02: 1473.276814248781148190 DAI
    # * Current price on sushiswap: 1472.650060106236758540 DAI
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

    order_list = orderbook.database.list_orders(status=OrderStatus.active)
    assert len(order_list) == 1

    await orderbook.find_opportunities()

    order_list = orderbook.database.list_orders(status=OrderStatus.executed)
    assert len(order_list) == 1

    assert weth9.balance_of(orderbook.web3.eth.default_account) == int(0)
    assert dai.balance_of(orderbook.web3.eth.default_account) == int(1517024094830368309726)
