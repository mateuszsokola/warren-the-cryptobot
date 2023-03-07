import pytest
from web3 import Web3
from exchanges.uniswap.v3.models.quote_exact_input_params import QuoteExactInputParams
from exchanges.uniswap.v3.quoter_v2 import UniswapV3QuoterV2


@pytest.mark.asyncio
async def test_quoter_v2(web3: Web3):
    quoter_v2 = UniswapV3QuoterV2(web3=web3, address="0x61fFE014bA17989E743c5F6cB21bF9697530B21e")

    amount_in = int(1517024094830368309726)
    path = [
        "0x514910771AF9Ca656af840dff83E8264EcF986CA",  # LINK
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH9
        "0x6B175474E89094C44Da98b954EedeAC495271d0F",  # DAI
    ]

    params = QuoteExactInputParams(
        path=path,
        fees=[3000, 3000],
        amount_in=amount_in,
    )
    quotation = quoter_v2.quote_exact_input(params=params)
    assert quotation.amount_out == 223115816825122575781
