import asyncio
from typing import List

from web3 import Web3
from web3_utils.divide_chunks import divide_chunks
from oracle.contract_explorers.swapcat_explorer import SwapcatExplorer
from oracle.contract_explorers.token_explorer import TokenExplorer
from oracle.contract_explorers.uniswap_v2_explorer import UniswapV2Explorer
from oracle.core.flash_query import FlashQuery
from oracle.core.store import Store

from oracle.utils.load_contract_abi import load_contract_abi
from oracle.utils.logger import logger
from oracle.utils.to_hashmap import to_hashmap

SUSHISWAP_ROUTER = "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"
SUSHISWAP_FACTORY = "0xc35DADB65012eC5796536bD9864eD8773aBc74C4"

LEVINSWAP_ROUTER = "0xb18d4f69627F8320619A696202Ad2C430CeF7C53"
LEVINSWAP_FACTORY = "0x965769C9CeA8A7667246058504dcdcDb1E2975A5"

SWAPCAT = "0xB18713Ac02Fc2090c0447e539524a5c76f327a3b"


class BlockWatcher:
    def __init__(self, web3: Web3, store: Store, flash_query: FlashQuery):
        self.web3 = web3
        self.store = store
        self.flash_query = flash_query
        self.last_processed_block = 0

        self.token_explorer = TokenExplorer(web3=web3, store=store,)

        self.levinswap = UniswapV2Explorer(
            web3=web3,
            store=store,
            flash_query=flash_query,
            token_explorer=self.token_explorer,
            name="levinswap",
            router_address=LEVINSWAP_ROUTER,
            factory_address=LEVINSWAP_FACTORY,
        )
        self.sushiswap = UniswapV2Explorer(
            web3=web3,
            store=store,
            flash_query=flash_query,
            token_explorer=self.token_explorer,
            name="sushiswap",
            router_address=SUSHISWAP_ROUTER,
            factory_address=SUSHISWAP_FACTORY,
        )
        self.swapcat_explorer = SwapcatExplorer(web3=web3, store=store, token_explorer=self.token_explorer, name="swapcat", address=SWAPCAT)

    async def initial_sync(self):
        latest_block = self.web3.eth.get_block("latest")
        block_number = latest_block["number"]

        await asyncio.gather(
            self.swapcat_explorer.sync(block_number),
            self.sushiswap.sync_pairs(block_number),
            self.levinswap.sync_pairs(block_number),
        )

        await self.watch(latest_block)

    async def watch(self, start_from_block: int = 0):
        # current_block = self.web3.eth.get_block(27040660)
        # current_block = self.web3.eth.get_block(27040566)
        # latest_block = self.web3.eth.get_block(27056019)
        latest_block = self.web3.eth.get_block("latest")
        if latest_block == self.last_processed_block:
            return

        for block_number in range(start_from_block, latest_block["number"], 1):
            latest_block = self.web3.eth.get_block(block_number)
            logger.info(f"Checking block {block_number}")

            for tx_hash in latest_block["transactions"]:
                tx = self.web3.eth.get_transaction(tx_hash)
                if tx["from"] == LEVINSWAP_ROUTER or tx["to"] == LEVINSWAP_ROUTER:
                    self.levinswap.process_tx(tx["input"], block_number)
                    continue
                if tx["from"] == SUSHISWAP_ROUTER or tx["to"] == SUSHISWAP_ROUTER:
                    self.sushiswap.process_tx(tx["input"], block_number)
                    continue
                if tx["from"] == SWAPCAT or tx["to"] == SWAPCAT:
                    self.swapcat_explorer.process_tx(tx["input"], block_number)
                    continue

            self.last_processed_block = block_number

        current_block = self.web3.eth.get_block("latest")
        if latest_block["number"] < current_block["number"]:
            self.watch(latest_block["number"])
