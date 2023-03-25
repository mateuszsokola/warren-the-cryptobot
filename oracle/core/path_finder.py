from typing import List, Tuple

from web3 import Web3
from oracle.core.store import Store
from oracle.utils.calculate_amount_out import calculate_token0_to_token1_amount_out, calculate_token1_to_token0_amount_out

USDC = "0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83"


class PathFinder:
    def __init__(self, store: Store):
        self.store = store

    def find_path(self, token: str, max_amount: int, max_hops: int = 3):
        if max_hops == 0:
            return None

        return

    def find(self, path: List[str], amounts: List[int], remaining_hops: int = 3):
        if remaining_hops == 0:
            return None

        assert len(path) > 0
        assert len(path) == len(amounts) + 1

        token_in = path[len(path) - 1]
        amount_in = amounts[len(amounts) - 1]

        pairs = self.store.list_uniswap_v2_pairs_by_token(token=token_in)
        # print("len(pairs)", len(pairs))
        result: List[Tuple[List[str], List[int]]] = []
        for pair in pairs:
            amount_out = None
            token_out = None
            if pair.token0 == token_in:
                amount_out = calculate_token1_to_token0_amount_out(
                    reserve0=int(pair.reserve0),
                    reserve1=int(pair.reserve1),
                    amount_in=amount_in,
                )
                token_out = pair.token1
            else:
                amount_out = calculate_token0_to_token1_amount_out(
                    reserve0=int(pair.reserve0),
                    reserve1=int(pair.reserve1),
                    amount_in=amount_in,
                )
                token_out = pair.token0

            path.append(token_out)
            amounts.append(amount_out)

            if token_out == USDC:
                # print(pair.type)
                # print(pair.address)
                # print("reserve0", int(pair.reserve0))
                # print("reserve1", int(pair.reserve1))
                result.append((path, amounts))
            else:
                return self.find(path=path, amounts=amounts, remaining_hops=(remaining_hops - 1))

        return result
