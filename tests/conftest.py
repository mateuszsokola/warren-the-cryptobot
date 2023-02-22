import asyncio
import pytest
from brownie import accounts
from web3 import Web3, AsyncHTTPProvider, HTTPProvider
from web3.eth import AsyncEth, Eth
from web3.main import get_default_modules
from web3.net import AsyncNet
from warren.managers.transaction_manager import TransactionManager
from warren.utils.retryable_eth_module import retryable_eth_module


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def bot():
    return accounts[0]


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
def transaction_service(web3: Web3, async_web3: Web3) -> TransactionManager:
    return TransactionManager(web3=web3, async_web3=async_web3)
