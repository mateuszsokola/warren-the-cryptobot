import pytest
from decimal import Decimal
from exchanges.uniswap.v3.models.exact_input_single_params import ExactInputSingleParams
from exchanges.uniswap.v3.pool import UniswapV3Pool
from exchanges.uniswap.v3.router import UniswapV3Router
from tokens.dai import DAI
from tokens.weth9 import WETH9
from grid_trading.models.strategy_dto import StrategyDto
from grid_trading.models.strategy_status import StrategyStatus
from grid_trading.core.grid_trading_service import GridTradingService
from warren.services.transaction_service import TransactionService
from warren.utils.to_wei import to_wei


@pytest.mark.asyncio
async def test_sell_orders(grid_trading: GridTradingService, transaction_service: TransactionService):
    uniswap_v3_router_address = "0xE592427A0AEce92De3Edee1F18E0157C05861564"

    dai = DAI(web3=grid_trading.web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F")
    weth9 = WETH9(web3=grid_trading.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

    # current price = 1517024094830368309726
    reference_price = to_wei(Decimal(1400), decimals=DAI.decimals())
    mock_strategy = StrategyDto(
        token0=weth9,
        token1=dai,
        reference_price=int(reference_price),
        last_tx_price=None,
        grid_every_percent=Decimal(0.05),
        percent_per_flip=Decimal(0.25),
        status=StrategyStatus.active,
    )
    grid_trading.database.create_grid_trading_order(order=mock_strategy)

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

    assert weth9.balance_of(grid_trading.web3.eth.default_account) == int(1000000000000000000)
    assert dai.balance_of(grid_trading.web3.eth.default_account) == int(0)

    strategy_list = grid_trading.database.list_grid_trading_orders(status=StrategyStatus.active)
    assert len(strategy_list) == 1

    await grid_trading.find_opportunities()

    strategy_list = grid_trading.database.list_grid_trading_orders(status=StrategyStatus.active)
    assert len(strategy_list) == 1

    assert weth9.balance_of(grid_trading.web3.eth.default_account) == int(750000000000000000)
    assert dai.balance_of(grid_trading.web3.eth.default_account) == int(379282133433460463304)


@pytest.mark.asyncio
async def test_buy_orders(grid_trading: GridTradingService, transaction_service: TransactionService):
    uniswap_v3_router_address = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
    sushi_router_address = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"

    uniswap_v3_pool = UniswapV3Pool(web3=grid_trading.web3, address="0xC2e9F25Be6257c210d7Adf0D4Cd6E3E881ba25f8")
    uniswap_v3_router = UniswapV3Router(web3=grid_trading.web3, address=uniswap_v3_router_address)

    dai = DAI(web3=grid_trading.web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F")
    weth9 = WETH9(web3=grid_trading.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

    # current price = 1517024094830368309726
    reference_price = to_wei(Decimal(1800), decimals=DAI.decimals())
    mock_strategy = StrategyDto(
        token0=weth9,
        token1=dai,
        reference_price=int(reference_price),
        last_tx_price=None,
        grid_every_percent=Decimal(0.05),
        percent_per_flip=Decimal(0.25),
        status=StrategyStatus.active,
    )
    grid_trading.database.create_grid_trading_order(order=mock_strategy)

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

    assert weth9.balance_of(grid_trading.web3.eth.default_account) == int(1000000000000000000)
    assert dai.balance_of(grid_trading.web3.eth.default_account) == int(0)

    params = ExactInputSingleParams(
        token_in=weth9.address,
        token_out=dai.address,
        fee=uniswap_v3_pool.fee(),
        amount_in=amount_in,
        amount_out_minimum=0,
        recipient=grid_trading.web3.eth.default_account,
        deadline=99999999999999,
        sqrt_price_limit_x96=0,
    )
    await transaction_service.send_transaction(
        uniswap_v3_router.exact_input_single(params, fees.gas_limit, fees.max_fee_per_gas, fees.max_fee_per_gas)
    )

    assert weth9.balance_of(grid_trading.web3.eth.default_account) == int(0)
    assert dai.balance_of(grid_trading.web3.eth.default_account) == int(1517024094830368309726)

    await transaction_service.send_transaction(
        dai.approve(
            sushi_router_address,
            max_amount_in=int(1517024094830368309726),
            gas_limit=fees.gas_limit,
            max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
            max_fee_per_gas=fees.max_fee_per_gas,
        )
    )

    strategy_list = grid_trading.database.list_grid_trading_orders(status=StrategyStatus.active)
    assert len(strategy_list) == 1

    await grid_trading.find_opportunities()

    strategy_list = grid_trading.database.list_grid_trading_orders(status=StrategyStatus.active)
    assert len(strategy_list) == 1

    assert weth9.balance_of(grid_trading.web3.eth.default_account) == int(248931433622879918)
    assert dai.balance_of(grid_trading.web3.eth.default_account) == int(1137768071122776232295)


@pytest.mark.asyncio
async def test_multiple_orders(grid_trading: GridTradingService, transaction_service: TransactionService):
    uniswap_v3_router_address = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
    sushi_router_address = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"

    dai = DAI(web3=grid_trading.web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F")
    weth9 = WETH9(web3=grid_trading.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

    # current price = 1517024094830368309726
    reference_price = to_wei(Decimal(1400), decimals=DAI.decimals())
    mock_strategy = StrategyDto(
        token0=weth9,
        token1=dai,
        reference_price=int(reference_price),
        last_tx_price=None,
        grid_every_percent=Decimal(0.05),
        percent_per_flip=Decimal(0.25),
        status=StrategyStatus.active,
    )
    grid_trading.database.create_grid_trading_order(order=mock_strategy)

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
    await transaction_service.send_transaction(
        dai.approve(
            sushi_router_address,
            max_amount_in=int(1517024094830368309726),
            gas_limit=fees.gas_limit,
            max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
            max_fee_per_gas=fees.max_fee_per_gas,
        )
    )

    assert weth9.balance_of(grid_trading.web3.eth.default_account) == int(1000000000000000000)
    assert dai.balance_of(grid_trading.web3.eth.default_account) == int(0)

    strategy_list = grid_trading.database.list_grid_trading_orders(status=StrategyStatus.active)
    strategy = strategy_list[0]
    assert strategy is not None

    # Sell order
    await grid_trading.find_opportunities()

    assert weth9.balance_of(grid_trading.web3.eth.default_account) == int(750000000000000000)
    assert dai.balance_of(grid_trading.web3.eth.default_account) == int(379282133433460463304)

    grid_trading.database.change_grid_trading_order_last_tx_price(strategy.id, last_tx_price=int(1800 * 10**18))

    strategy_list = grid_trading.database.list_grid_trading_orders(status=StrategyStatus.active)

    # Buy order
    await grid_trading.find_opportunities()

    strategy_list = grid_trading.database.list_grid_trading_orders(status=StrategyStatus.active)

    assert weth9.balance_of(grid_trading.web3.eth.default_account) == int(812241974468099649)
    assert dai.balance_of(grid_trading.web3.eth.default_account) == int(284461600075095347478)

    # Sell order
    grid_trading.database.change_grid_trading_order_last_tx_price(strategy.id, last_tx_price=int(1400 * 10**18))

    await grid_trading.find_opportunities()

    assert weth9.balance_of(grid_trading.web3.eth.default_account) == int(609181480851074737)
    assert dai.balance_of(grid_trading.web3.eth.default_account) == int(592517657383009985662)

    # Sell order
    grid_trading.database.change_grid_trading_order_last_tx_price(strategy.id, last_tx_price=int(1400 * 10**18))

    await grid_trading.find_opportunities()

    assert weth9.balance_of(grid_trading.web3.eth.default_account) == int(456886110638306053)
    assert dai.balance_of(grid_trading.web3.eth.default_account) == int(823552164224990140454)
