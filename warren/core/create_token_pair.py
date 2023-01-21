from web3 import Web3
from warren.core.uniswap_v3_token_pair import UniswapV3TokenPair
from warren.models.token_pair import TokenPair
from warren.services.base_token_pair import BaseTokenPair
from warren.services.transaction_service import TransactionService

from warren.tokens.dai import Dai
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
        )
    else:
        return None
