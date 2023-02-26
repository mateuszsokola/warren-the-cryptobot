from web3 import Web3
from warren.utils.load_contract_abi import load_contract_abi


def get_tokens_from_address(web3: Web3, address: str):
    contract = web3.eth.contract(
        address=address,
        abi=load_contract_abi("IMooniswap.json", "artifacts/mooniswap"),
    )

    return contract.functions.getTokens().call()
