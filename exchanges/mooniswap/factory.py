from typing import List
from web3 import Web3
from warren.utils.load_contract_abi import load_contract_abi


class MooniSwapFactory:
    def __init__(self, web3: Web3, address: str):
        self.web3 = web3

        self.address = address
        self.contract = web3.eth.contract(
            address=address,
            abi=load_contract_abi("IMooniFactory.json", "artifacts/mooniswap"),
        )

    def get_all_pools(self) -> List[str]:
        pools = self.contract.functions.getAllPools().call()

        return pools
