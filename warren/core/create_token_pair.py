from web3 import Web3
from warren.core.uniswap_v3_token_pair import UniswapV3TokenPair
from warren.models.token_pair import TokenPair
from warren.services.base_token_pair import BaseTokenPair
from warren.services.transaction_service import TransactionService

from warren.tokens.dai import Dai
from warren.tokens.wbtc import WBtc
from warren.tokens.weth9 import WEth9


def create_token_pair(
    async_web3: Web3,
    web3: Web3,
    transaction_service: TransactionService,
    token_pair: TokenPair,
) -> BaseTokenPair:
    if token_pair.value == "WETH9/DAI":
        token_in = WEth9(web3=web3, transaction_service=transaction_service)
        token_out = Dai(web3=web3, transaction_service=transaction_service)

        return UniswapV3TokenPair(
            async_web3=async_web3,
            web3=web3,
            transaction_service=transaction_service,
            token_in=token_in,
            token_out=token_out,
            min_balance_to_transact=100000000000000,
        )
    elif token_pair.value == "DAI/WETH9":
        token_in = Dai(web3=web3, transaction_service=transaction_service)
        token_out = WEth9(web3=web3, transaction_service=transaction_service)

        return UniswapV3TokenPair(
            async_web3=async_web3,
            web3=web3,
            transaction_service=transaction_service,
            token_in=token_in,
            token_out=token_out,
            min_balance_to_transact=100000000000000,
        )
    if token_pair.value == "WETH9/WBTC":
        token_in = WEth9(web3=web3, transaction_service=transaction_service)
        token_out = WBtc(web3=web3, transaction_service=transaction_service)

        return UniswapV3TokenPair(
            async_web3=async_web3,
            web3=web3,
            transaction_service=transaction_service,
            token_in=token_in,
            token_out=token_out,
            min_balance_to_transact=100000000000000,
        )
    if token_pair.value == "WBTC/WETH9":
        token_in = WBtc(web3=web3, transaction_service=transaction_service)
        token_out = WEth9(web3=web3, transaction_service=transaction_service)

        return UniswapV3TokenPair(
            async_web3=async_web3,
            web3=web3,
            transaction_service=transaction_service,
            token_in=token_in,
            token_out=token_out,
            min_balance_to_transact=1000,
        )
    else:
        return None
