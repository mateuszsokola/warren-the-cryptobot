from web3 import Web3

from warren.utils.load_contract_abi import load_contract_abi

uniswap_v3_pool_address = "0xC2e9F25Be6257c210d7Adf0D4Cd6E3E881ba25f8"


class UniswapV3Pool:
    def __init__(self, web3: Web3, address: str):
        self.web3 = web3
        self.address = address
        self.contract = web3.eth.contract(
            address=address,
            abi=load_contract_abi("IUniswapV3Pool.json", "artifacts/uniswap/v3"),
        )

    def fee(self):
        return self.contract.functions.fee().call()
