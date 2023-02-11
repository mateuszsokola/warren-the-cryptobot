from typing import List, Tuple
from tokens.base_token import BaseToken
from warren.core.base_token_pair import BaseTokenPair


class ExchangeManager:
    _exchange_list: List[BaseTokenPair] = []
    token0: BaseToken
    token1: BaseToken
    # TODO(mateu.sh): implement caching per block
    _block_number: int = 0
    _prices: List[Tuple[BaseTokenPair, int, int]] = []
    highest_price: Tuple[BaseTokenPair, int, int] = None
    lowest_price: Tuple[BaseTokenPair, int, int] = None

    def __init__(self, exchange_list: List[BaseTokenPair], token0: BaseToken, token1: BaseToken):
        self._exchange_list = exchange_list
        self.token0 = token0
        self.token1 = token1

        self._prices = self._fetch_prices()

    def retrieve_prices(self) -> List[Tuple[BaseTokenPair, int, int]]:
        return self._prices


    def _fetch_prices(self):
        result: List[Tuple(BaseTokenPair, int)] = []

        for exchange in self._exchange_list:
            price = None

            if self.token0.name == exchange.token0.name:
                price = exchange.calculate_token0_to_token1_amount_out()
            else:
                price = exchange.calculate_token1_to_token0_amount_out()

            pricepoint = (exchange, int(1 * 10 ** self.token0.decimals()), price)

            if self.highest_price is None or self.highest_price[2] < pricepoint[2]: 
                self.highest_price = pricepoint

            if self.lowest_price is None or self.lowest_price[2] > pricepoint[2]: 
                self.lowest_price = pricepoint

            result.append(pricepoint)

        return result
