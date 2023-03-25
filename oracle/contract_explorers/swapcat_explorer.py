import asyncio
from typing import List
from web3 import Web3
from oracle.contract_explorers.token_explorer import TokenExplorer

from oracle.core.store import Store
from oracle.models.swapcat.offer import SwapcatOffer
from oracle.utils.load_contract_abi import load_contract_abi
from oracle.utils.logger import logger


class SwapcatExplorer:
    buy_fn_signature = Web3.toHex(Web3.keccak(text="buy(uint24,uint256,uint256)"))[2:10]
    makeoffer_fn_signature = Web3.toHex(Web3.keccak(text="makeoffer(address,address,uint256,uint24)"))[2:10]
    deleteoffer_fn_signature = Web3.toHex(Web3.keccak(text="deleteoffer(uint24)"))[2:10]

    def __init__(self, web3: Web3, store: Store, token_explorer: TokenExplorer, address: str, name: str):
        self.web3 = web3
        self.store = store
        self.name = name
        self.token_explorer = token_explorer
        self.contract = web3.eth.contract(
            Web3.toChecksumAddress(address),
            abi=load_contract_abi("ISWAPCAT.json"),
        )

    def process_tx(self, input: str, block_number: int) -> List:
        fn_signature = input[2:10]

        if self.buy_fn_signature == fn_signature:
            (_, payload) = self.contract.decode_function_input(input)
            try:
                self._create_or_update_offer(payload["_offerid"], block_number=block_number)
            except Exception as exc:
                logger.error(f"SwapcatExplorer - buy - {payload} - {exc}")
            finally:
                return
        elif self.makeoffer_fn_signature == fn_signature:
            self.sync(block_number=block_number)
            return
        elif self.deleteoffer_fn_signature == fn_signature:
            (_, payload) = self.contract.decode_function_input(input)
            self.store.remove_offer(payload["_offerid"], block_number=block_number)
            return
        else:
            # do nothing
            return

    async def sync(self, block_number: int):
        offer_count = self.contract.functions.getoffercount().call()
        last_idx = 9900

        if offer_count > last_idx + 1:
            for idx in range(last_idx, offer_count, 1):
                try:
                    self._create_or_update_offer(idx, block_number)
                except:
                    continue
                finally:
                    await asyncio.sleep(0)

    def _create_or_update_offer(self, idx: int, block_number: int):
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

        self.token_explorer.discover_token(offer_tuple[0])
        self.token_explorer.discover_token(offer_tuple[1])

        if offer.available_balance > 0:
            self.store.insert_or_replace_offer(offer, True)
            logger.info(f"{self.name} - Offer {idx}")
