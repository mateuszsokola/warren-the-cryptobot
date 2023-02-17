import pytest
from brownie import accounts, chain
from web3 import Web3, AsyncHTTPProvider, HTTPProvider
from web3.eth import AsyncEth, Eth
from web3.main import get_default_modules
from web3.net import AsyncNet

from grid_trading.services.grid_trading_service import GridTradingService
from warren.core.database import Database
from warren.utils.retryable_eth_module import retryable_eth_module


@pytest.fixture(scope="module")
def grid_trading() -> GridTradingService:
    database = Database(database_file=":memory:")
    eth1_api_url = "http://127.0.0.1:8545"

    async_web3 = Web3(
        AsyncHTTPProvider(eth1_api_url),
        modules={
            "eth": (retryable_eth_module(AsyncEth),),
            "net": (AsyncNet,),
        },
        middlewares=[],
    )
    web3_modules = get_default_modules()
    web3_modules["eth"] = retryable_eth_module(Eth)
    web3 = Web3(HTTPProvider(eth1_api_url), modules=web3_modules)

    account = accounts[0]
    web3.eth.default_account = account.address

    return GridTradingService(
        async_web3=async_web3,
        web3=web3,
        database=database,
    )


@pytest.fixture(autouse=True)
def isolation(fn_isolation, grid_trading):
    # before tests create blockchain snapshot
    chain.snapshot()

    # tests are happening here
    yield

    grid_trading.latest_checked_block = 0
    grid_trading.database.cur.execute("DELETE FROM grid_trading_orders")
    grid_trading.database.con.commit()
    # after tests revert to initial blockchain snapshot
    chain.revert()
