from typing import List
from web3 import Web3

from oracle.core.store import Store
from oracle.models.swapcat.offer import SwapcatOffer
from oracle.utils.load_contract_abi import load_contract_abi
from oracle.utils.logger import logger


SWAPCAT = "0x1d871cd7EB915A36cC5C83F4151AC4a229231212"


class SwapcatExplorer:
    buy_fn_signature = Web3.toHex(Web3.keccak(text="buy(uint24,uint256,uint256)"))[2:10]
    makeoffer_fn_signature = Web3.toHex(Web3.keccak(text="makeoffer(address,address,uint256,uint24)"))[2:10]
    deleteoffer_fn_signature = Web3.toHex(Web3.keccak(text="deleteoffer(uint24)"))[2:10]

    def __init__(self, web3: Web3, store: Store):
        self.web3 = web3
        self.store = store
        self.contract = web3.eth.contract(
            Web3.toChecksumAddress(SWAPCAT),
            abi=load_contract_abi("ISWAPCAT.json"),
        )

    def process_tx(self, input: str, block_number: int) -> List:
        fn_signature = input[2:10]

        if self.buy_fn_signature == fn_signature:
            (_, payload) = self.contract.decode_function_input(input)
            self._create_or_update_offer(payload["_offerid"], True)
            return
        elif self.makeoffer_fn_signature == fn_signature:
            (_, payload) = self.contract.decode_function_input(input)
            print("AAAA", payload)
            self._create_or_update_offer(payload["_offerid"], True)
            return
        elif self.deleteoffer_fn_signature == fn_signature:
            (_, payload) = self.contract.decode_function_input(input)
            self.store.remove_offer(payload["_offerid"], True)
            return
        else:
            # do nothing
            return

    def _create_or_update_offer(self, idx: int, block_number: int):
        print("BBBB")
        offer_tuple = self.contract.functions.showoffer(idx).call()
        print("BBBB")
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
            self.store.con.commit()

            logger.info(f"Offer #{idx}")
