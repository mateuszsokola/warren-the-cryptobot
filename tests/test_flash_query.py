import brownie
import pytest
from brownie import FlashQuery, accounts


def test_batch_offer_balances():
    deployer = accounts[0]

    flash_query = deployer.deploy(FlashQuery)

    offers = [9922, 9923, 9924, 9925]
    results = flash_query.batchOfferBalances(offers)

    assert len(results) == 4


def test_batch_reserves_by_pair():
    deployer = accounts[0]

    flash_query = deployer.deploy(FlashQuery)

    pairs = [
        "0xc358FB670c2dc2DA440DC87CA7146d7e1c4256c0",
        "0x331AbCE2e23E20196ebaba33Bafc366d9A66E723",
        "0x6E5F9bd90e3Ca508F9c3BDA23f25838e37c0A3Ac",
        "0x05D1885bae8482604bFa4E2018b98bb1cB67639E",
    ]
    results = flash_query.batchReservesByPairs(pairs)

    assert len(results) == 4
    print(results)
