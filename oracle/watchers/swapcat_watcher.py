from typing import List

from web3 import Web3
from web3.types import LogReceipt
from web3_utils.divide_chunks import divide_chunks
from oracle.core.flash_query import FlashQuery
from oracle.core.store import Store
from oracle.models.swapcat.offer import SwapcatOffer

from oracle.utils.load_contract_abi import load_contract_abi
from oracle.utils.runner import Runner
from oracle.utils.logger import logger
from oracle.utils.to_hashmap import to_hashmap


class SwapcatWatcher:
    def __init__(self, web3: Web3, address: str, store: Store, flash_query: FlashQuery):
        self.contract = web3.eth.contract(
            Web3.toChecksumAddress(address),
            abi=load_contract_abi("ISWAPCAT.json"),
        )

        self.flash_query = flash_query
        self.web3 = web3
        self.store = store

        self.store.create_sync_state_table("swapcat")

    async def sync(self):
        block = self.web3.eth.get_block("latest")
        offer_count = self.contract.functions.allPairsLength().call()

        last_idx = self.store.last_sync_state("swap")

        if offer_count > last_idx + 1:
            for idx in range(last_idx, offer_count, 1):
                try:
                    self._create_offer(idx, block["number"])
                except:
                    continue

    async def sync_balances(self):
        block = self.web3.eth.get_block("latest")

        offer_list = self.store.list_swapcat_offers()
        offers = to_hashmap(offer_list)
        index_list = list(o.id for o in offer_list)

        chunks = list(divide_chunks(index_list, 10))

        for chunk in chunks:
            logger.info(f"Processing chunk {len(chunk)}")
            available_balances = self.flash_query.batch_swapcat_offer_available_balances(chunk)

            for idx, offer_id in enumerate(chunk):
                offer = offers[offer_id]
                balance = available_balances[idx]

                if balance == 0:
                    self.store.remove_offer(offer)
                    continue

                offer.block_number = block["number"]
                offer.available_balance = balance
                self.store.insert_or_replace_offer(offer)

            self.store.con.commit()

    def _create_offer(self, idx: int, block_number: int):
        offer_tuple = self.contract.functions.showoffer(idx).call()
        offer = SwapcatOffer(
            id=idx,
            block_number=block_number,
            token0=offer_tuple[0],
            token1=offer_tuple[1],
            recipient=offer_tuple[2],
            amount=offer_tuple[3],
            available_balance=offer_tuple[4],
        )

        if offer.available_balance > 0:
            self.store.insert_or_replace_offer(offer)
            self.store.set_last_sync_state("swapcat", block_number, idx)
            self.store.con.commit()

            logger.info(f"Offer #{idx}")
