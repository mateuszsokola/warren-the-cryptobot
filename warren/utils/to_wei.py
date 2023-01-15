from decimal import Decimal


def to_wei(amount: Decimal, decimals: int = 18):
    return int(amount * 10**decimals)
