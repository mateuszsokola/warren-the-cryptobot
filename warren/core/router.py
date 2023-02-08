from fractions import Fraction
from typing import List
from web3 import Web3

from exchanges.uniswap.v2.models.get_pair_params import GetPairParams
from exchanges.uniswap.v2.factory import UniswapV2Factory
from exchanges.uniswap.v2.router import UniswapV2Router
from exchanges.uniswap.v3.pool import UniswapV3Pool
from exchanges.uniswap.v3.quoter_v2 import UniswapV3QuoterV2
from exchanges.uniswap.v3.router import UniswapV3Router
from tokens.dai import DAI
from tokens.usdc import USDC
from tokens.wbtc import WBTC
from tokens.weth9 import WETH9
from warren.core.base_token_pair import BaseTokenPair
from warren.core.uniswap_v2_token_pair import UniswapV2TokenPair
from warren.core.uniswap_v3_token_pair import UniswapV3TokenPair
from warren.models.exchange import BaseExchange, UniswapV2Exchange, UniswapV3Exchange
from warren.models.network import Network
from warren.models.base_token_pair import BaseTokenPairMetaV2, UniswapV2TokenPairMeta


class Router:
    def __init__(self, web3: Web3, async_web3: Web3):
        self.async_web3 = async_web3
        self.web3 = web3

    def get_exchange_list(self, network: Network = Network.Ethereum) -> List[BaseTokenPair]:
        result: List[BaseTokenPair] = []

        for exchange in self._get_exchanges(network):
            for token_pair in exchange.token_pairs:
                if isinstance(exchange, UniswapV2Exchange):
                    params = GetPairParams(token0=token_pair.token0.address, token1=token_pair.token1.address)
                    uniswap_v2_pair = exchange.uniswap_v2_factory.get_pair(params, fee=token_pair.fee)

                    result.append(
                        UniswapV2TokenPair(
                            web3=self.web3,
                            async_web3=self.async_web3,
                            name=exchange.name,
                            token0=token_pair.token0,
                            token1=token_pair.token1,
                            token_pair=uniswap_v2_pair,
                            router=exchange.uniswap_v2_router,
                        )
                    )
                elif isinstance(exchange, UniswapV3Exchange):
                    result.append(
                        UniswapV3TokenPair(
                            web3=self.web3,
                            async_web3=self.async_web3,
                            name=exchange.name,
                            token0=token_pair.token0,
                            token1=token_pair.token1,
                            pool=exchange.uniswap_v3_pool,
                            quoter=exchange.uniswap_v3_quoter,
                            router=exchange.uniswap_v3_router,
                        )
                    )
                else:
                    continue

        return result

    def _get_exchanges(self, network: Network = Network.Ethereum) -> List[BaseExchange]:
        map = {
            Network.Ethereum.value: [
                # uniswap_v3_quoter
                # UniswapV3Exchange(
                #     name="uniswap_v3_quoter",
                #     uniswap_v3_pool=UniswapV3Pool(web3=self.web3, address="0xC2e9F25Be6257c210d7Adf0D4Cd6E3E881ba25f8"),
                #     uniswap_v3_router=UniswapV3Router(web3=self.web3, address="0xE592427A0AEce92De3Edee1F18E0157C05861564"),
                #     uniswap_v3_quoter=UniswapV3Quoter(web3=self.web3, address="0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6"),
                #     token_pairs=[
                #         BaseTokenPairMetaV2(
                #             name="WETH9/DAI",
                #             token0=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                #             token1=DAI(web3=self.web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F"),
                #         ),
                #         BaseTokenPairMetaV2(
                #             name="WETH9/WBTC",
                #             token0=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                #             token1=WBTC(web3=self.web3, address="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"),
                #         ),
                #         BaseTokenPairMetaV2(
                #             name="WETH9/USDC",
                #             token0=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                #             token1=USDC(web3=self.web3, address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"),
                #         ),
                #         BaseTokenPairMetaV2(
                #             name="DAI/WETH9",
                #             token0=DAI(web3=self.web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F"),
                #             token1=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                #         ),
                #         BaseTokenPairMetaV2(
                #             name="WBTC/WETH9",
                #             token0=WBTC(web3=self.web3, address="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"),
                #             token1=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                #         ),
                #         BaseTokenPairMetaV2(
                #             name="USDC/WETH9",
                #             token0=USDC(web3=self.web3, address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"),
                #             token1=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                #         ),
                #     ],
                # ),
                # uniswap_v3_quoter_v2
                UniswapV3Exchange(
                    name="uniswap_v3_quoter_v2",
                    uniswap_v3_pool=UniswapV3Pool(web3=self.web3, address="0xC2e9F25Be6257c210d7Adf0D4Cd6E3E881ba25f8"),
                    uniswap_v3_router=UniswapV3Router(web3=self.web3, address="0xE592427A0AEce92De3Edee1F18E0157C05861564"),
                    uniswap_v3_quoter=UniswapV3QuoterV2(web3=self.web3, address="0x61fFE014bA17989E743c5F6cB21bF9697530B21e"),
                    token_pairs=[
                        BaseTokenPairMetaV2(
                            name="WETH9/DAI",
                            token0=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                            token1=DAI(web3=self.web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F"),
                        ),
                        BaseTokenPairMetaV2(
                            name="WETH9/WBTC",
                            token0=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                            token1=WBTC(web3=self.web3, address="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"),
                        ),
                        BaseTokenPairMetaV2(
                            name="WETH9/USDC",
                            token0=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                            token1=USDC(web3=self.web3, address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"),
                        ),
                        # BaseTokenPairMetaV2(
                        #     name="DAI/WETH9",
                        #     token0=DAI(web3=self.web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F"),
                        #     token1=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                        # ),
                        # BaseTokenPairMetaV2(
                        #     name="WBTC/WETH9",
                        #     token0=WBTC(web3=self.web3, address="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"),
                        #     token1=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                        # ),
                        # BaseTokenPairMetaV2(
                        #     name="USDC/WETH9",
                        #     token0=USDC(web3=self.web3, address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"),
                        #     token1=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                        # ),
                    ],
                ),
                # # uniswap_v2_router01
                # UniswapV2Exchange(
                #     name="uniswap_v2_router01",
                #     uniswap_v2_factory=UniswapV2Factory(web3=self.web3, address="0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"),
                #     uniswap_v2_router=UniswapV2Router(web3=self.web3, address="0xf164fC0Ec4E93095b804a4795bBe1e041497b92a"),
                #     token_pairs=[
                #         UniswapV2TokenPairMeta(
                #             name="WETH9/DAI",
                #             token0=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                #             token1=DAI(web3=self.web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F"),
                #             fee=Fraction(3, 100),
                #         ),
                #         UniswapV2TokenPairMeta(
                #             name="WETH9/WBTC",
                #             token0=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                #             token1=WBTC(web3=self.web3, address="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"),
                #             fee=Fraction(3, 100),
                #         ),
                #         UniswapV2TokenPairMeta(
                #             name="WETH9/USDC",
                #             token0=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                #             token1=USDC(web3=self.web3, address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"),
                #             fee=Fraction(3, 100),
                #         ),
                #     ],
                # ),
                # uniswap_v2_router02
                UniswapV2Exchange(
                    name="uniswap_v2_router02",
                    uniswap_v2_factory=UniswapV2Factory(web3=self.web3, address="0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"),
                    uniswap_v2_router=UniswapV2Router(web3=self.web3, address="0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"),
                    token_pairs=[
                        UniswapV2TokenPairMeta(
                            name="WETH9/DAI",
                            token0=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                            token1=DAI(web3=self.web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F"),
                            fee=Fraction(3, 100),
                        ),
                        UniswapV2TokenPairMeta(
                            name="WETH9/WBTC",
                            token0=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                            token1=WBTC(web3=self.web3, address="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"),
                            fee=Fraction(3, 100),
                        ),
                        UniswapV2TokenPairMeta(
                            name="WETH9/USDC",
                            token0=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                            token1=USDC(web3=self.web3, address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"),
                            fee=Fraction(3, 100),
                        ),
                    ],
                ),
                # pancakeswap
                UniswapV2Exchange(
                    name="pancakeswap",
                    uniswap_v2_factory=UniswapV2Factory(web3=self.web3, address="0x1097053Fd2ea711dad45caCcc45EfF7548fCB362"),
                    uniswap_v2_router=UniswapV2Router(web3=self.web3, address="0xEfF92A263d31888d860bD50809A8D171709b7b1c"),
                    token_pairs=[
                        UniswapV2TokenPairMeta(
                            name="WETH9/USDC",
                            token0=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                            token1=USDC(web3=self.web3, address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"),
                            fee=Fraction(25, 1000),
                        ),
                    ],
                ),
                # sushiswap
                UniswapV2Exchange(
                    name="sushiswap",
                    uniswap_v2_factory=UniswapV2Factory(web3=self.web3, address="0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"),
                    uniswap_v2_router=UniswapV2Router(web3=self.web3, address="0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"),
                    token_pairs=[
                        UniswapV2TokenPairMeta(
                            name="WETH9/DAI",
                            token0=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                            token1=DAI(web3=self.web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F"),
                            fee=Fraction(3, 100),
                        ),
                        UniswapV2TokenPairMeta(
                            name="WETH9/WBTC",
                            token0=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                            token1=WBTC(web3=self.web3, address="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"),
                            fee=Fraction(3, 100),
                        ),
                        UniswapV2TokenPairMeta(
                            name="WETH9/USDC",
                            token0=WETH9(web3=self.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                            token1=USDC(web3=self.web3, address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"),
                            fee=Fraction(3, 100),
                        ),
                    ],
                ),
            ]
        }

        return map[network.Ethereum.value]
