from fractions import Fraction
from web3 import Web3
from warren.utils.load_contract_abi import load_contract_abi


class UniswapV2Pair:
    def __init__(self, web3: Web3, address: str, token0: str, token1: str, fee: Fraction = Fraction(3, 1000)):
        self.web3 = web3

        self.address = address
        self.token0 = token0
        self.token1 = token1
        self.contract = web3.eth.contract(
            address=address,
            abi=load_contract_abi("Pair.json", "artifacts/uniswap/v2"),
        )

        self.fee = fee
        self._set_pair_inverted()

    def calculate_token0_to_token1_amount_out(self, amount_in: int) -> int:
        (reserve0, reserve1, timestamp) = self.contract.functions.getReserves().call()

        amount_in_with_fee = amount_in * (self.fee.denominator - self.fee.numerator)
        numerator = amount_in_with_fee * reserve0
        denominator = reserve1 * self.fee.denominator + amount_in_with_fee

        return numerator // denominator

    def calculate_token1_to_token0_amount_out(self, amount_in: int) -> int:
        (reserve0, reserve1, timestamp) = self.contract.functions.getReserves().call()

        amount_in_after_fee = amount_in * (self.fee.denominator - self.fee.numerator)
        numerator = amount_in_after_fee * reserve1
        denominator = reserve0 * self.fee.denominator + amount_in_after_fee

        return numerator // denominator

    def _set_pair_inverted(self):
        token0 = self.contract.functions.token0().call()
        self.pair_inverted = token0 == self.token0
