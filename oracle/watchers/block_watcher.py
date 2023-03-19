from typing import List

from web3 import Web3
from web3.types import LogReceipt
from web3_utils.divide_chunks import divide_chunks
from oracle.contract_explorers.swapcat_explorer import SwapcatExplorer
from oracle.contract_explorers.uniswap_v2_explorer import UniswapV2Explorer
from oracle.core.flash_query import FlashQuery
from oracle.core.store import Store
from oracle.models.swapcat.offer import SwapcatOffer

from oracle.utils.load_contract_abi import load_contract_abi
from oracle.utils.runner import Runner
from oracle.utils.logger import logger
from oracle.utils.to_hashmap import to_hashmap

SUSHISWAP_ROUTER = "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"

SWAPCAT = "0xB18713Ac02Fc2090c0447e539524a5c76f327a3b"


class BlockWatcher:
    def __init__(self, web3: Web3, store: Store, flash_query: FlashQuery):
        self.web3 = web3
        self.store = store
        self.flash_query = flash_query
        self.last_processed_block = 0

        self.sushiswap = UniswapV2Explorer(web3=web3, store=store, flash_query=flash_query)
        self.swapcat_explorer = SwapcatExplorer(web3=web3, store=store)

    # async def watch(self):
    #     # current_block = self.web3.eth.get_block(27040660)
    #     # current_block = self.web3.eth.get_block(27040566)
    #     latest_block = self.web3.eth.get_block("latest")
    #     for block_number in range(27031449, latest_block["number"], 1):
    #         for tx_hash in latest_block["transactions"]:
    #             tx = self.web3.eth.get_transaction(tx_hash)
    #             if tx["from"] == SUSHISWAP_ROUTER or tx["to"] == SUSHISWAP_ROUTER:
    #                 self.sushiswap.process_tx(tx["input"], block_number)
    #                 continue
    #             if tx["from"] == SWAPCAT or tx["to"] == SWAPCAT:
    #                 self.swapcat_explorer.process_tx(tx["input"], block_number)
    #                 continue

    async def watch(self):
        # current_block = self.web3.eth.get_block(27040660)
        # current_block = self.web3.eth.get_block(27040566)
        # latest_block = self.web3.eth.get_block(27056019)
        latest_block = self.web3.eth.get_block("latest")
        for block_number in range(27055374, latest_block["number"], 1):
            latest_block = self.web3.eth.get_block(block_number)
            logger.info(f"Checking block {block_number}")

            for tx_hash in latest_block["transactions"]:
                tx = self.web3.eth.get_transaction(tx_hash)
                if tx["from"] == SUSHISWAP_ROUTER or tx["to"] == SUSHISWAP_ROUTER:
                    self.sushiswap.process_tx(tx["input"], block_number)
                    continue
                if tx["from"] == SWAPCAT or tx["to"] == SWAPCAT:
                    self.swapcat_explorer.process_tx(tx["input"], block_number)
                    continue
