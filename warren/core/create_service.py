from eth_account.signers.local import LocalAccount
from web3.middleware import (
    construct_sign_and_send_raw_middleware,
    time_based_cache_middleware,
    simple_cache_middleware,
)
from web3 import Web3, AsyncHTTPProvider, HTTPProvider
from web3.eth import AsyncEth, Eth
from web3.main import get_default_modules
from web3.net import AsyncNet
from grid_trading.core.grid_trading_service import GridTradingService
from warren.core.database import Database
from warren.core.setup_wizard import SetupWizard
from warren.managers.config_manager import ConfigManager
from warren.models.option_name import OptionName
from warren.models.service import Service
from order_book.core.order_book_service import OrderBookService
from warren.utils.retryable_eth_module import retryable_eth_module


def create_service(config_path: str, passphrase: str = "") -> Service:
    database_file = SetupWizard.database_file_path(config_path)
    database = Database(database_file=database_file)

    config = ConfigManager(database=database)
    eth_api_url = config.options.get(OptionName.eth_api_url)

    async_web3 = Web3(
        AsyncHTTPProvider(eth_api_url),
        modules={
            "eth": (retryable_eth_module(AsyncEth),),
            "net": (AsyncNet,),
        },
        middlewares=[],
    )
    web3_modules = get_default_modules()
    web3_modules["eth"] = retryable_eth_module(Eth)
    web3 = Web3(HTTPProvider(eth_api_url), modules=web3_modules)

    geth_file = SetupWizard.geth_file_path(config_path)
    with open(geth_file) as keyfile:
        encrypted_key = keyfile.read()
        private_key = web3.eth.account.decrypt(encrypted_key, passphrase)

    account: LocalAccount = web3.eth.account.from_key(private_key)
    print(f"Loaded address = {account.address}")

    web3.eth.default_account = account.address
    web3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
    """
    Caches responses based on the whitelisted rpc requests in
    TIME_BASED_CACHE_RPC_WHITELIST for 15 seconds.
    """
    web3.middleware_onion.add(time_based_cache_middleware)
    """
    Avoids re-fetching whitelisted rpc methods in SIMPLE_CACHE_RPC_WHITELIST.
    """
    web3.middleware_onion.add(simple_cache_middleware)

    return Service(
        async_web3=async_web3,
        web3=web3,
        config=config,
        database=database,
    )
