from fractions import Fraction
from typing import List
from web3 import Web3

from exchanges.uniswap.v2.models.get_pair_params import GetPairParams
from exchanges.uniswap.v2.factory import UniswapV2Factory
from exchanges.uniswap.v2.router import UniswapV2Router
from exchanges.uniswap.v3.pool import UniswapV3Pool
from exchanges.uniswap.v3.quoter_v2 import UniswapV3QuoterV2
from exchanges.uniswap.v3.router import UniswapV3Router
from tokens.base_token import BaseToken
from warren.core.base_token_pair import BaseTokenPair
from warren.core.token import Token
from warren.core.uniswap_v2_token_pair import UniswapV2TokenPair
from warren.core.uniswap_v3_token_pair import UniswapV3TokenPair
from warren.models.network import Network
from warren.utils.load_yaml import load_yaml


class Router:
    _pairs: List[BaseTokenPair] = []

    def __init__(
        self, web3: Web3, async_web3: Web3, token: Token, network: Network = Network.Ethereum, filename: str = "./routes.yml"
    ):
        self.async_web3 = async_web3
        self.web3 = web3
        self.token = token

        self._pairs = self._load_exchanges(filename=filename, network=network)

    def get_token_pairs(self) -> List[BaseTokenPair]:
        return self._pairs

    def get_token_pair_by_token0_and_token1(self, token0: BaseToken, token1: BaseToken) -> List[BaseTokenPair]:
        result = []

        for pair in self._pairs:
            a = pair.token0.name == token0.name and pair.token1.name == token1.name
            b = pair.token0.name == token1.name and pair.token1.name == token0.name
            if a or b:
                result.append(pair)

        return result

    def get_token_routes(self) -> dict[str, List[str]]:
        result: dict[str, List[str]] = {}

        for exchange in self._pairs:
            token0_name = exchange.token0.name
            token1_name = exchange.token1.name

            if token0_name not in result.keys():
                result[token0_name] = []

            if token1_name not in result.keys():
                result[token1_name] = []

            if token1_name not in result[token0_name]:
                result[token0_name].append(token1_name)

            if token0_name not in result[token1_name]:
                result[token1_name].append(token0_name)

        return result

    def _load_exchanges(self, filename: str, network: Network = Network.Ethereum):
        result: List[BaseTokenPair] = []

        file_content = load_yaml(filename)
        # TODO(mateu.sh): add asserts to every record
        for exchange_meta in file_content[network.value.lower()]:
            for pair in exchange_meta["pairs"]:
                instance = None
                token0 = self.token.get_token_by_name(pair["token0"].upper())
                token1 = self.token.get_token_by_name(pair["token1"].upper())

                if exchange_meta["type"] == "uniswap_v2":
                    factory = UniswapV2Factory(web3=self.web3, address=exchange_meta["addresses"]["factory"])
                    params = GetPairParams(token0=token0.address, token1=token1.address)
                    fee = Fraction(exchange_meta["meta"]["fee"]["numerator"], exchange_meta["meta"]["fee"]["denumerator"])
                    uniswap_v2_pair = factory.get_pair(params, fee=fee)

                    instance = UniswapV2TokenPair(
                        web3=self.web3,
                        async_web3=self.async_web3,
                        name=exchange_meta["name"],
                        token0=token0,
                        token1=token1,
                        token_pair=uniswap_v2_pair,
                        router=UniswapV2Router(web3=self.web3, address=exchange_meta["addresses"]["router"]),
                        # TODO(mateu.sh): parametrize
                        min_balance_to_transact=0,
                    )
                elif exchange_meta["type"] == "uniswap_v3":
                    instance = UniswapV3TokenPair(
                        web3=self.web3,
                        async_web3=self.async_web3,
                        name=exchange_meta["name"],
                        token0=token0,
                        token1=token1,
                        pool=UniswapV3Pool(web3=self.web3, address=exchange_meta["addresses"]["pool"]),
                        router=UniswapV3Router(web3=self.web3, address=exchange_meta["addresses"]["router"]),
                        quoter=UniswapV3QuoterV2(web3=self.web3, address=exchange_meta["addresses"]["quoter_v2"]),
                        # TODO(mateu.sh): parametrize
                        min_balance_to_transact=0,
                    )
                else:
                    continue

                result.append(instance)

        return result
