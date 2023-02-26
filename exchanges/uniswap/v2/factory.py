from fractions import Fraction
from web3 import Web3
from exchanges.uniswap.v2.models.get_pair_params import GetPairParams
from exchanges.uniswap.v2.pair import UniswapV2Pair
from warren.utils.load_contract_abi import load_contract_abi


class UniswapV2Factory:
    def __init__(self, web3: Web3, address: str):
        self.web3 = web3

        self.address = address
        self.contract = web3.eth.contract(
            address=address,
            abi=load_contract_abi("Factory.json", "artifacts/uniswap/v2"),
        )

    def get_pair(self, params: GetPairParams, fee: Fraction = Fraction(3, 1000)) -> UniswapV2Pair:
        address = self.contract.functions.getPair(
            params.token0,
            params.token1,
        ).call()

        return UniswapV2Pair(web3=self.web3, address=address, token0=params.token0, token1=params.token1, fee=fee)

    def get_pairs_length(self) -> int:
        return self.contract.functions.allPairsLength().call()

    def get_pair_address_by_index(self, index: int) -> str:
        return self.contract.functions.allPairs(index).call()
