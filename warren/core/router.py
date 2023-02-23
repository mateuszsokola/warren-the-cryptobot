from fractions import Fraction
from typing import List
from web3 import Web3

from exchanges.stableswap.tripool import StableSwap3pool
from exchanges.uniswap.v2.models.get_pair_params import GetPairParams
from exchanges.uniswap.v2.factory import UniswapV2Factory
from exchanges.uniswap.v2.router import UniswapV2Router
from exchanges.uniswap.v3.pool import UniswapV3Pool
from exchanges.uniswap.v3.quoter_v2 import UniswapV3QuoterV2
from exchanges.uniswap.v3.router import UniswapV3Router
from tokens.base_token import BaseToken
from warren.core.token import Token
from warren.routes.base_route import BaseRoute
from warren.routes.stableswap_3pool_route import StableSwap3poolRoute
from warren.routes.uniswap_v2 import UniswapV2Route
from warren.routes.uniswap_v3 import UniswapV3Route
from warren.models.network import Network
from warren.utils.load_yaml import load_yaml


class Router:
    routes: List[BaseRoute] = []

    def __init__(self, web3: Web3, async_web3: Web3, token: Token, filename: str = "./routes.yml"):
        self.async_web3 = async_web3
        self.web3 = web3
        self.token = token

        self.routes = self._load_exchanges(filename=filename)

    def get_token_pairs(self) -> List[BaseRoute]:
        return self.routes

    def get_routes_by_token0_and_token1(self, token0: BaseToken, token1: BaseToken) -> List[BaseRoute]:
        result = []

        for route in self.routes:
            has_token0 = False
            has_token1 = False

            for token in route.tokens:
                if token0.name == token.name:
                    has_token0 = True

                if token1.name == token.name:
                    has_token1 = True

            if has_token0 and has_token1:
                result.append(route)

        return result

    def get_all_tokens(self) -> List[str]:
        result: List[str] = []

        for route in self.routes:
            for token in route.tokens:
                if token.name not in result:
                    result.append(token.name)

        return result

    def get_all_tokens_by_token0(self, token0: BaseToken) -> List[str]:
        result: List[str] = []

        for route in self.routes:
            if token0 in route.tokens:
                for token in route.tokens:
                    if token.name not in result and token0.name != token.name:
                        result.append(token.name)

        return result

    def _load_exchanges(self, filename: str, network: Network = Network.Ethereum):
        file_content = load_yaml(filename)

        result: List[BaseRoute] = []
        for exchange_meta in file_content[network.value.lower()]:
            if exchange_meta["type"] == "stableswap_3pool":
                tokens: List[BaseToken] = []

                for token in exchange_meta["tokens"]:
                    tokens.append(self.token.get_token_by_name(token.upper()))

                instance = StableSwap3poolRoute(
                    web3=self.web3,
                    async_web3=self.async_web3,
                    name=exchange_meta["name"],
                    tokens=tokens,
                    pool=StableSwap3pool(web3=self.web3, address=exchange_meta["addresses"]["pool"]),
                )

                result.append(instance)

            elif exchange_meta["type"] == "uniswap_v2":
                for pair in exchange_meta["pairs"]:
                    token0 = self.token.get_token_by_name(pair["token0"].upper())
                    token1 = self.token.get_token_by_name(pair["token1"].upper())

                    factory = UniswapV2Factory(web3=self.web3, address=exchange_meta["addresses"]["factory"])
                    params = GetPairParams(token0=token0.address, token1=token1.address)
                    fee = Fraction(exchange_meta["meta"]["fee"]["numerator"], exchange_meta["meta"]["fee"]["denumerator"])
                    uniswap_v2_pair = factory.get_pair(params, fee=fee)

                    instance = UniswapV2Route(
                        web3=self.web3,
                        async_web3=self.async_web3,
                        name=exchange_meta["name"],
                        tokens=[token0, token1],
                        pair=uniswap_v2_pair,
                        router=UniswapV2Router(web3=self.web3, address=exchange_meta["addresses"]["router"]),
                    )

                    result.append(instance)

            elif exchange_meta["type"] == "uniswap_v3":
                for pair in exchange_meta["pairs"]:
                    token0 = self.token.get_token_by_name(pair["token0"].upper())
                    token1 = self.token.get_token_by_name(pair["token1"].upper())
                    instance = UniswapV3Route(
                        web3=self.web3,
                        async_web3=self.async_web3,
                        name=exchange_meta["name"],
                        tokens=[token0, token1],
                        pool=UniswapV3Pool(web3=self.web3, address=exchange_meta["addresses"]["pool"]),
                        router=UniswapV3Router(web3=self.web3, address=exchange_meta["addresses"]["router"]),
                        quoter=UniswapV3QuoterV2(web3=self.web3, address=exchange_meta["addresses"]["quoter_v2"]),
                    )

                    result.append(instance)

            else:
                continue

        return result
