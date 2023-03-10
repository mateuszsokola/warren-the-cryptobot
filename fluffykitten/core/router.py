from fractions import Fraction
from typing import List
from web3 import Web3

from fluffykitten.routes.base_route import BaseRoute
from fluffykitten.routes.uniswap_v2_route import UniswapV2Route
from fluffykitten.routes.uniswap_v3_route import UniswapV3Route
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
            if exchange_meta["type"] == "uniswap_v2":
                fees = []
                for fee in exchange_meta["fees"]:
                    fees.append(Fraction(fee["numerator"], fee["denumerator"]))

                instance = UniswapV2Route(
                    web3=self.web3,
                    async_web3=self.async_web3,
                    name=exchange_meta["name"],
                    factory_address=exchange_meta["addresses"]["factory"],
                    router_address=exchange_meta["addresses"]["router"],
                    path=exchange_meta["path"],
                    fees=fees,
                )

                result.append(instance)

            elif exchange_meta["type"] == "uniswap_v3":
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
