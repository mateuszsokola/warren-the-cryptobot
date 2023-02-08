# import pytest
# from warren.core.create_token_pair import create_token_pair
# from warren.models.token_pair import TokenPair
# from warren.services.order_book_service import OrderBookService
# from warren.tokens.dai import Dai
# from warren.tokens.weth9 import WEth9
# from warren.uniswap.v3.router import uniswap_v3_router_address


# @pytest.mark.asyncio
# async def test_dai_weth9(orderbook: OrderBookService):
#     weth9 = WEth9(web3=orderbook.web3, transaction_service=orderbook.transaction_service)
#     amount_in = int(2 * 10**18)
#     await weth9.deposit(amount_in=amount_in)
#     await weth9.approve(uniswap_v3_router_address, max_amount_in=amount_in)

#     uniswap_v3_weth9_dai_pair = create_token_pair(
#         async_web3=orderbook.async_web3,
#         web3=orderbook.web3,
#         transaction_service=orderbook.transaction_service,
#         token_pair=TokenPair.weth9_dai,
#     )

#     (weth9_balance, dai_balance) = uniswap_v3_weth9_dai_pair.balances()
#     assert weth9_balance == int(2000000000000000000)
#     assert dai_balance == int(0)

#     await uniswap_v3_weth9_dai_pair.swap(amount_in=int(1 * 10**18))

#     (weth9_balance, dai_balance) = uniswap_v3_weth9_dai_pair.balances()
#     assert weth9_balance == int(1000000000000000000)
#     assert dai_balance == int(1517024094830368309726)

#     dai = Dai(web3=orderbook.web3, transaction_service=orderbook.transaction_service)
#     await dai.approve(uniswap_v3_router_address, max_amount_in=dai_balance)

#     uniswap_v3_dai_weth9_pair = create_token_pair(
#         async_web3=orderbook.async_web3,
#         web3=orderbook.web3,
#         transaction_service=orderbook.transaction_service,
#         token_pair=TokenPair.dai_weth9,
#     )

#     await uniswap_v3_dai_weth9_pair.swap(amount_in=dai_balance)

#     (dai_balance, weth9_balance) = uniswap_v3_dai_weth9_pair.balances()
#     assert weth9_balance == int(1994009273709804490)
#     assert dai_balance == int(0)
