import pytest
from decimal import Decimal
from grid_trading.utils.create_grid import create_grid


def test_create_grid():
    percent = Decimal(5) / Decimal(100)
    reference_price = int(1500 * 10**18)
    grid = create_grid(reference_price, percent)

    assert grid == (1462500000000000000000, 1537500000000000000000)
