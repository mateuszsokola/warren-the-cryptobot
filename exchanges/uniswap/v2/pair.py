from fractions import Fraction
from web3 import Web3
from warren.services.transaction_service import TransactionService
from warren.utils.load_contract_abi import load_contract_abi


class UniswapV2Pair:
    def __init__(self, web3: Web3, address: str, fee: Fraction = Fraction(3, 1000)):
        self.web3 = web3

        self.address = address
        self.contract = web3.eth.contract(
            address=address,
            abi=load_contract_abi("Pair.json", "artifacts/uniswap/v2"),
        )

        self.fee = fee

    def get_price(self, amount_in: int) -> int:
        (reserve0, reserve1, timestamp) = self.contract.functions.getReserves().call()

        amount_in_with_fee = amount_in * (self.fee.denominator - self.fee.numerator)

        # this should be correct!!!
        # numerator = amount_in_with_fee * reserve1
        # denominator = reserve0 * self.fee.denominator + amount_in_with_fee
        numerator = amount_in_with_fee * reserve0
        denominator = reserve1 * self.fee.denominator + amount_in_with_fee

        return numerator // denominator
