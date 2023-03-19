from typing import List

from web3 import Web3
from oracle.models.flash_query.uniswap_v2_pair_reserves import UniswapV2PairReserves
from oracle.utils.load_contract_abi import load_contract_abi


class FlashQuery:
    def __init__(self, web3: Web3, address: str):
        self.contract = web3.eth.contract(
            Web3.toChecksumAddress(address),
            abi=load_contract_abi("FlashQuery.json", "build/contracts"),
        )

    def batch_swapcat_offer_available_balances(self, offer_ids: List[int]) -> List[int]:
        return self.contract.functions.batchOfferBalances(offer_ids).call()

    def batch_reserves_by_pairs(self, pair_addresses: List[str]) -> List[UniswapV2PairReserves]:
        result = self.contract.functions.batchReservesByPairs(pair_addresses).call()

        res: List[UniswapV2PairReserves] = []

        for idx, (reserve0, reserve1, timestamp) in enumerate(result):
            pair = UniswapV2PairReserves(
                address=pair_addresses[idx],
                reserve0=reserve0,
                reserve1=reserve1,
                timestamp=timestamp,
            )
            res.append(pair)

        return res
