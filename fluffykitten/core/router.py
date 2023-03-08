from fractions import Fraction
from typing import List
from web3 import Web3

from exchanges.mooniswap.mooniswap import MooniSwap
from exchanges.stableswap.tripool import StableSwap3pool
from exchanges.uniswap.v2.models.get_pair_params import GetPairParams
from exchanges.uniswap.v2.factory import UniswapV2Factory
from exchanges.uniswap.v2.router import UniswapV2Router
from exchanges.uniswap.v3.pool import UniswapV3Pool
from exchanges.uniswap.v3.quoter_v2 import UniswapV3QuoterV2
from exchanges.uniswap.v3.router import UniswapV3Router
from fluffykitten.routes.uniswap_v3_route import UniswapV3Route
from tokens.base_token import BaseToken
from warren.core.token import Token
from warren.routes.base_route import BaseRoute
from warren.routes.mooniswap_route import MooniswapRoute
from warren.routes.stableswap_3pool_route import StableSwap3poolRoute
from warren.routes.uniswap_v2 import UniswapV2Route
from warren.models.network import Network
from warren.utils.load_yaml import load_yaml


class Router:
    routes: List[BaseRoute] = []

    def __init__(self, web3: Web3, async_web3: Web3, filename: str = "./fluffykitten/routes.yml"):
        self.async_web3 = async_web3
        self.web3 = web3

        self.routes = self._load_routes(filename=filename)

    def list_routes(self) -> List[BaseRoute]:
        return self.routes

    def _load_routes(self, filename: str, network: Network = Network.Ethereum):
        file_content = load_yaml(filename)

        result: List[BaseRoute] = []
        for exchange_meta in file_content[network.value.lower()]:
            if exchange_meta["type"] == "uniswap_v3":
                instance = UniswapV3Route(
                    web3=self.web3,
                    async_web3=self.async_web3,
                    name=exchange_meta["name"],
                    quoter_address=exchange_meta["addresses"]["quoter_v2"],
                    router_address=exchange_meta["addresses"]["router"],
                    path=exchange_meta["path"],
                    fees=exchange_meta["fees"],
                )

                result.append(instance)

            else:
                continue

        return result
