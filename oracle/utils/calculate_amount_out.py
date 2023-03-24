from fractions import Fraction


def calculate_token0_to_token1_amount_out(reserve0: int, reserve1: int, amount_in: int, fee: Fraction = Fraction(3, 1000)) -> int:
    amount_in_after_fee = amount_in * (fee.denominator - fee.numerator)
    numerator = amount_in_after_fee * reserve1
    denominator = reserve0 * fee.denominator + amount_in_after_fee

    return numerator // denominator


def calculate_token1_to_token0_amount_out(reserve0: int, reserve1: int, amount_in: int, fee: Fraction = Fraction(3, 1000)) -> int:
    amount_in_with_fee = amount_in * (fee.denominator - fee.numerator)
    numerator = amount_in_with_fee * reserve0
    denominator = reserve1 * fee.denominator + amount_in_with_fee

    return numerator // denominator
