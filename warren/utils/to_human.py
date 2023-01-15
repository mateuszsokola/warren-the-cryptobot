from decimal import Decimal


def to_human(amount: Decimal, decimals: int = 18) -> Decimal:
    return Decimal(amount) / Decimal(10**decimals)
