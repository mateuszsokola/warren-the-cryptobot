import pytest
from warren.utils.to_human import to_human


def test_do_not_use_scientific_format():
    assert to_human(10 * 10**18, decimals=18) == "10.000000000000000000"
    assert to_human(10 * 10**9, decimals=9) == "10.000000000"
    assert to_human(10 * 10**2, decimals=2) == "10.00"
