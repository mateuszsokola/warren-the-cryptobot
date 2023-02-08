import pytest
from brownie import accounts, chain
from web3 import Web3, AsyncHTTPProvider, HTTPProvider
from web3.eth import AsyncEth, Eth
from web3.main import get_default_modules
from web3.net import AsyncNet
from warren.services.transaction_service import TransactionService
from warren.utils.retryable_eth_module import retryable_eth_module


@pytest.fixture(scope="module")
def web3() -> Web3:
    eth1_api_url = "http://127.0.0.1:8545"

    web3_modules = get_default_modules()
    web3_modules["eth"] = retryable_eth_module(Eth)
    web3 = Web3(HTTPProvider(eth1_api_url), modules=web3_modules)

    account = accounts[0]
    web3.eth.default_account = account.address

    return web3


@pytest.fixture(scope="module")
def async_web3() -> Web3:
    eth1_api_url = "http://127.0.0.1:8545"

    async_web3 = Web3(
        AsyncHTTPProvider(eth1_api_url),
        modules={
            "eth": (retryable_eth_module(AsyncEth),),
            "net": (AsyncNet,),
        },
        middlewares=[],
    )

    return async_web3


@pytest.fixture(scope="module")
def transaction_service(web3: Web3, async_web3: Web3) -> TransactionService:
    return TransactionService(web3=web3, async_web3=async_web3)


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    # before tests create blockchain snapshot
    chain.snapshot()

    # tests are happening here
    yield

    # after tests revert to initial blockchain snapshot
    chain.revert()
