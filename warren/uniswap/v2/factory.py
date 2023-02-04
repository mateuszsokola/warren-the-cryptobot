from fractions import Fraction
from web3 import Web3
from warren.services.transaction_service import TransactionService
from warren.uniswap.v2.models.get_pair_params import GetPairParams
from warren.uniswap.v2.pair import UniswapV2Pair
from warren.utils.load_contract_abi import load_contract_abi


class UniswapV2Factory:
    def __init__(self, web3: Web3, transaction_service: TransactionService, address: str):
        self.web3 = web3
        self.transaction_service = transaction_service

        self.address = address
        self.contract = web3.eth.contract(
            address=address,
            abi=load_contract_abi("Factory.json", "artifacts/uniswap/v2"),
        )

    def get_pair(self, params: GetPairParams, fee: Fraction = Fraction(3, 1000)) -> UniswapV2Pair:
        address = self.contract.functions.getPair(
            params.token_in,
            params.token_out,
        ).call()

        return UniswapV2Pair(web3=self.web3, transaction_service=self.transaction_service, address=address, fee=fee)
