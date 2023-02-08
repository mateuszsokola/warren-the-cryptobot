import pytest
from brownie import chain


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    # before tests create blockchain snapshot
    chain.snapshot()

    # tests are happening here
    yield

    # after tests revert to initial blockchain snapshot
    chain.revert()
