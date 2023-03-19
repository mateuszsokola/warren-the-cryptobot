from typing import List

from web3 import Web3
from web3_utils.divide_chunks import divide_chunks
from oracle.core.flash_query import FlashQuery
from oracle.core.store import Store
from oracle.models.uniswap.pair import UniswapV2PairDto

from oracle.utils.load_contract_abi import load_contract_abi
from oracle.utils.logger import logger
from oracle.utils.to_hashmap import to_hashmap


def create_pair_from_address(web3: Web3, address: str):
    contract = web3.eth.contract(
        address=address,
        abi=load_contract_abi("IUniswapV2Pair.json"),
    )

    token0 = contract.functions.token0().call()
    token1 = contract.functions.token1().call()
    (reserve0, reserve1, timestamp) = contract.functions.getReserves().call()

    return (token0, token1, reserve0, reserve1, timestamp)


class UniswapV2Watcher:
    def __init__(self, web3: Web3, address: str, name: str, store: Store, flash_query: FlashQuery):
        self.contract = web3.eth.contract(
            Web3.toChecksumAddress(address),
            abi=load_contract_abi("IUniswapV2Factory.json"),
        )

        self.flash_query = flash_query
        self.web3 = web3
        self.name = name
        self.store = store

        self.store.create_sync_state_table(name.lower())

    async def sync(self):
        block = self.web3.eth.get_block("latest")
        pair_count = self.contract.functions.allPairsLength().call()
        last_idx = self.store.last_sync_state(self.name.lower())

        if pair_count > last_idx + 1:
            for idx in range(0, pair_count, 1):
                address = self.contract.functions.allPairs(idx).call()

                (token0, token1, reserve0, reserve1, timestamp) = create_pair_from_address(web3=self.web3, address=address)
                pair = UniswapV2PairDto(
                    type=self.name,
                    address=address,
                    token0=token0,
                    token1=token1,
                    reserve0=reserve0,
                    reserve1=reserve1,
                    timestamp=timestamp,
                )
                self.store.insert_or_replace_pair(pair)
                self.store.set_last_sync_state(self.name.lower(), block["number"], idx)
                self.store.con.commit()

                logger.info(f"Pair #{idx} on {self.name}")

    # async def sync_reserves(self):
    #     block = self.web3.eth.get_block("latest")

    #     pair_list = self.store.list_uniswap_v2_pairs()
    #     pairs = to_hashmap(pair_list)
    #     address_list = list(o.address for o in pair_list)

    #     chunks = list(divide_chunks(address_list, 10))

    #     for chunk in chunks:
    #         logger.info(f"Processing chunk {len(chunk)}")
    #         available_balances = self.flash_query.batch_reserves_by_pairs(chunk)

    #         for idx, address in enumerate(chunk):
    #             pair = pairs[pair_id]
    #             balance = available_balances[idx]

    #             self.store.insert_or_replace_pair(pair)

    #         self.store.con.commit()
