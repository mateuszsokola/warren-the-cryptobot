from decimal import Decimal


def create_grid(reference_price: int, grid_every_percent: Decimal):
    delta = Decimal(reference_price) * grid_every_percent

    upper = int(reference_price + delta / 2)
    lower = int(reference_price - delta / 2)

    return (lower, upper)
