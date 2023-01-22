from decimal import Decimal


def to_human(amount: Decimal, decimals: int = 18) -> Decimal:
    value = Decimal(amount) / Decimal(10**decimals)
    format = "{" + f":.{decimals}f" + "}"
    return format.format(value)
