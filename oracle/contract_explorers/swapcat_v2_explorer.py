import asyncio
from typing import List
from web3 import Web3
from oracle.contract_explorers.token_explorer import TokenExplorer

from oracle.core.store import Store
from oracle.models.swapcat.offer import SwapcatOffer, SwapcatV2Offer
from oracle.utils.load_contract_abi import load_contract_abi
from oracle.utils.logger import logger


class SwapcatV2Explorer:
    buy_fn_signature = Web3.toHex(Web3.keccak(text="buy(uint256,uint256,uint256)"))[2:10]
    buyOfferBatch_fn_signature = Web3.toHex(Web3.keccak(text="buyOfferBatch(uint256[],uint256[],uint256[])"))[2:10]
    buyWithPermit_fn_signature = Web3.toHex(
        Web3.keccak(text="buyWithPermit(uint256,uint256,uint256,uint256,uint8,bytes32,bytes32)")
    )[2:10]
    createOffer_fn_signature = Web3.toHex(Web3.keccak(text="createOffer(address,address,address,uint256,uint256)"))[2:10]
    createOfferBatch_fn_signature = Web3.toHex(
        Web3.keccak(text="createOfferBatch(address[],address[],address[],uint256[],uint256[])")
    )[2:10]
    createOfferWithPermit_fn_signature = Web3.toHex(
        Web3.keccak(text="createOfferWithPermit(address,address,address,uint256,uint256,uint256,uint256,uint8,bytes32,bytes32)")
    )[2:10]
    deleteOffer_fn_signature = Web3.toHex(Web3.keccak(text="deleteOffer(uint256)"))[2:10]
    deleteOfferBatch_fn_signature = Web3.toHex(Web3.keccak(text="deleteOfferBatch(uint256[])"))[2:10]
    deleteOfferByAdmin_fn_signature = Web3.toHex(Web3.keccak(text="deleteOfferByAdmin(uint256[])"))[2:10]
    # grantrole
    # initialize
    # pause
    # renounceRole
    # revokeRole
    # saveLostTokens
    # setFee
    # toggleWhitelistWithType
    # unpause
    updateOffer_fn_signature = Web3.toHex(Web3.keccak(text="updateOffer(uint256,uint256,uint256)"))[2:10]
    updateOfferBatch_fn_signature = Web3.toHex(Web3.keccak(text="updateOfferBatch(uint256[],uint256[],uint256[])"))[2:10]
    updateOfferWithPermit_fn_signature = Web3.toHex(
        Web3.keccak(text="updateOfferWithPermit(uint256,uint256,uint256,uint256,uint256,uint8,bytes32,bytes32)")
    )[2:10]
    # upgradeTo
    # upgradeToAndCall

    def __init__(self, web3: Web3, store: Store, token_explorer: TokenExplorer, address: str, name: str):
        self.web3 = web3
        self.store = store
        self.name = name
        self.token_explorer = token_explorer
        self.contract = web3.eth.contract(
            Web3.toChecksumAddress(address),
            abi=load_contract_abi("IRealTokenYamUpgradeableV3.json"),
        )

        self.create_fns = [
            self.createOffer_fn_signature,
            self.createOfferBatch_fn_signature,
            self.createOfferWithPermit_fn_signature,
        ]
        self.delete_fns = [self.deleteOffer_fn_signature, self.deleteOfferBatch_fn_signature, self.deleteOfferByAdmin_fn_signature]
        self.buy_or_update_fns = [
            self.buy_fn_signature,
            # self.buyOfferBatch_fn_signature,
            self.buyWithPermit_fn_signature,
            self.updateOffer_fn_signature,
            self.updateOfferBatch_fn_signature,
            self.updateOfferWithPermit_fn_signature,
        ]

    def process_tx(self, input: str, block_number: int) -> List:
        fn_signature = input[2:10]

        if fn_signature in self.buy_or_update_fns:
            (_, payload) = self.contract.decode_function_input(input)
            try:
                self._create_or_update_offer(payload["offerId"], block_number=block_number)
            except Exception as exc:
                logger.error(f"SwapcatV2Explorer - buy - {payload} - {exc}")
            finally:
                return
        elif fn_signature in self.create_fns:
            (_, payload) = self.contract.decode_function_input(input)

            last_idx = self.store.find_last_id("swapcat_v2_offers")
            # self.sync(block_number=block_number, last_idx=last_idx)
            return
        elif fn_signature in self.delete_fns:
            (_, payload) = self.contract.decode_function_input(input)
            self.store.remove_offer(payload["offerId"], block_number=block_number, table="swapcat_v2_offers", should_commit=True)
            return
        else:
            # do nothing
            return

    async def sync(self, block_number: int, last_idx: int = 0):
        offer_count = self.contract.functions.getOfferCount().call()
        if offer_count > last_idx + 1:
            for idx in range(last_idx, offer_count, 1):
                try:
                    self._create_or_update_offer(idx, block_number)
                except:
                    continue
                finally:
                    await asyncio.sleep(0)

    def _create_or_update_offer(self, idx: int, block_number: int):
        offer_tuple = self.contract.functions.showOffer(idx).call()
        offer = SwapcatV2Offer(
            id=idx,
            block_number=block_number,
            token0=offer_tuple[0],
            token1=offer_tuple[1],
            recipient=offer_tuple[2],
            unknown_address=offer_tuple[3],
            amount=offer_tuple[4],
            available_balance=offer_tuple[5],
        )

        self.token_explorer.discover_token(offer_tuple[0])
        self.token_explorer.discover_token(offer_tuple[1])

        if offer.available_balance > 0:
            self.store.insert_or_replace_swapcat_v2_offer(offer, True)
            logger.info(f"{self.name} - Offer {idx}")
