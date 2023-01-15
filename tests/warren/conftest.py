import pytest
from brownie import accounts, chain
from web3 import Web3, AsyncHTTPProvider, HTTPProvider
from web3.eth import AsyncEth, Eth
from web3.main import get_default_modules
from web3.net import AsyncNet

from warren.core.database import Database
from warren.services.order_book_service import OrderBookService
from warren.services.transaction_service import TransactionService
from warren.utils.retryable_eth_module import retryable_eth_module
from warren.services.order_book_service import OrderBookService


@pytest.fixture(scope="module")
def orderbook() -> OrderBookService:
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

    transaction_service = TransactionService(
        async_web3=async_web3,
        web3=web3,
    )

    return OrderBookService(
        async_web3=async_web3,
        web3=web3,
        database=database,
        transaction_service=transaction_service,
    )


@pytest.fixture(autouse=True)
def isolation(fn_isolation, orderbook):
    # before tests create blockchain snapshot
    chain.snapshot()

    # tests are happening here
    yield

    orderbook.latest_checked_block = 0
    orderbook.database.cur.execute("DELETE FROM order_book")
    orderbook.database.con.commit()
    # after tests revert to initial blockchain snapshot
    chain.revert()
