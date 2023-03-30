from eth_account.signers.local import LocalAccount
from web3 import Web3
from oracle.core.flash_query import FlashQuery
from oracle.core.store import Store
from oracle.watchers.block_watcher import BlockWatcher
from oracle.watchers.swapcat_watcher import SwapcatWatcher
from oracle.watchers.uniswap_v2_watcher import UniswapV2Watcher


class Oracle:
    """
    Oracle is a facade class aggregating all the ETH1 & ETH2 stakefish related functionalities
    """

    def __init__(self, web3: Web3, async_web3: Web3, account: LocalAccount):
        self.web3 = web3
        self.async_web3 = async_web3
        self.store = Store("./database.dat")
        self.account = account

        self.flash_query = FlashQuery(
            web3,
            address="0xC1C54429f96D9A475AAF9FE38Bd9cB5aEF3Ba675",
        )
        self.swapcat_watcher = SwapcatWatcher(
            web3,
            address="0xB18713Ac02Fc2090c0447e539524a5c76f327a3b",
            store=self.store,
            flash_query=self.flash_query,
        )
        self.sushiswap = UniswapV2Watcher(
            web3,
            address="0xc35DADB65012eC5796536bD9864eD8773aBc74C4",
            name="sushiswap",
            store=self.store,
            flash_query=self.flash_query,
        )
        self.levinswap = UniswapV2Watcher(
            web3,
            address="0x965769C9CeA8A7667246058504dcdcDb1E2975A5",
            name="levinswap",
            store=self.store,
            flash_query=self.flash_query,
        )

        self.block_watcher = BlockWatcher(web3=web3, store=self.store, flash_query=self.flash_query)

    async def initial_sync(self):
        await self.block_watcher.initial_sync()

    async def swapcat_sync_balances(self):
        await self.swapcat_watcher.sync_balances()

    async def initial_sync_sushiswap(self):
        await self.sushiswap.sync()

    async def initial_sync_levinwap(self):
        await self.levinswap.sync()

    async def watch_blocks(self):
        await self.block_watcher.watch()
