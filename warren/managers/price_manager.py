from typing import List, Tuple
from tokens.base_token import BaseToken
from warren.routes.base_route import BaseRoute


class PriceManager:
    route_list: List[BaseRoute] = []
    token0: BaseToken
    token1: BaseToken
    # TODO(mateu.sh): implement caching per block
    _block_number: int = 0
    _prices: List[Tuple[BaseRoute, int, int]] = []
    highest_price: Tuple[BaseRoute, int, int] = None
    lowest_price: Tuple[BaseRoute, int, int] = None

    def __init__(self, route_list: List[BaseRoute], token0: BaseToken, token1: BaseToken):
        self.route_list = route_list
        self.token0 = token0
        self.token1 = token1

        self._prices = self._fetch_prices()

    def retrieve_prices(self) -> List[Tuple[BaseRoute, int, int]]:
        return self._prices

    def _fetch_prices(self):
        result: List[Tuple(BaseRoute, int)] = []

        amount_in = int(1 * 10 ** self.token0.decimals())

        for exchange in self.route_list:
            price = exchange.calculate_amount_out(token0=self.token0, token1=self.token1, amount_in=amount_in)

            pricepoint = (exchange, amount_in, price)

            if self.highest_price is None or self.highest_price[2] < pricepoint[2]:
                self.highest_price = pricepoint

            if self.lowest_price is None or self.lowest_price[2] > pricepoint[2]:
                self.lowest_price = pricepoint

            result.append(pricepoint)

        return result
