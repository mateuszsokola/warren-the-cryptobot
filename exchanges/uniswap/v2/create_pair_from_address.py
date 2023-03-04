from web3 import Web3
from warren.utils.load_contract_abi import load_contract_abi


def create_pair_from_address(web3: Web3, address: str):
    contract = web3.eth.contract(
        address=address,
        abi=load_contract_abi("Pair.json", "artifacts/uniswap/v2"),
    )

    return contract
