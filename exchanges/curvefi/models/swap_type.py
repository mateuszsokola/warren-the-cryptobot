from enum import Enum


"""
The swap type should be
1 for a stableswap `exchange`,
2 for stableswap `exchange_underlying`,
3 for a cryptoswap `exchange`,
4 for a cryptoswap `exchange_underlying`,
5 for factory metapools with lending base pool `exchange_underlying`,
6 for factory crypto-meta pools underlying exchange (`exchange` method in zap),
7-11 for wrapped coin (underlying for lending pool) -> LP token "exchange" (actually `add_liquidity`),
12-14 for LP token -> wrapped coin (underlying for lending or fake pool) "exchange" (actually `remove_liquidity_one_coin`)
15 for WETH -> ETH "exchange" (actually deposit/withdraw)    
"""


class SwapType(int, Enum):
    stableswap_exchange = 1
    stableswap_exchange_underlying = 2
    cryptoswap_exchange = 3
    cryptoswap_exchange_underlying = 4
    factory_metapools_lending_pool_exchange = 5
    factory_crypto_metapools_exchange_underlying = 6
    weth_eth_exchange = 15
