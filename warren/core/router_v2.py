import itertools
from networkx import MultiGraph, all_shortest_paths
from typing import Any, Dict, List

from warren.models.network import Network
from warren.utils.load_yaml import load_yaml

from warren.models.network import Network
from warren.models.pools.base_pool import BasePool
from warren.models.pools.curvefi_pool import CurveFiPool
from warren.models.pools.pool_type import PoolType
from warren.utils.load_yaml import load_yaml

class A:
    pool_address: str 
    pool_type: str
    token0: str 
    token1: str


class RouterV2:
    graph: MultiGraph = MultiGraph()

    pools_by_type: Dict[PoolType, List[BasePool]] = {
        [PoolType.curvefi]: [],
    }


    def __init__(self):
        self._load_routes(filename="./metadata/pools/curvefi.yml")

    def get_routes_by_token0_and_token1(self, token0: str, token1: str) -> List:
        paths = list(all_shortest_paths(self.graph, token0, token1))
        global_result = []
        for tokens in paths:
            tokens_len = len(tokens)
            local_result = []
            for i in range(0, tokens_len, 1):
                partial = []

                if (i + 1 < tokens_len):
                    token_a = tokens[i]
                    token_b = tokens[i + 1]

                    edge_data = self.graph.get_edge_data(token_a, token_b)

                    for idx in edge_data:
                        edge = edge_data[idx]
                        if edge["token0"] == token_a and edge["token1"] == token_b:
                            partial.append(edge)

                if len(partial) > 0:
                    local_result.append(partial)
            
            global_result.append(local_result)

        result = []
        for path in global_result:
            route = []
            
            for edge in path:
                route.append(edge[0])

            result.append(route)

        return result
    

    def create_route(self, result: List):
        route: List[str] = []
        swap_type: List[List[int]] = []

        for path in result:
            return None


    def _load_routes(self, filename: str, network: Network = Network.Ethereum):
        file_content = load_yaml(filename)

        for pool_meta in file_content[network.value.lower()]:
            tokens = pool_meta["tokens"]
            pool_address = pool_meta["addresses"]["pool"]

            permutations = list(itertools.permutations(tokens, 2))

            for pair in permutations:
                self.graph.add_edge(
                    pair[0],
                    pair[1],
                    pool_address=pool_address,
                    pool_type=pool_meta["type"],
                    token0=pair[0],
                    token1=pair[1],
                )

            if pool_meta["type"] == "curvefi":
                pool = self._create_curvefi_pool(pool_meta=pool_meta)
                self.pools_by_type[PoolType.curvefi].append(pool)
            else:
                continue                

    def _create_curvefi_pool(self, pool_meta: Any) -> BasePool:
        pool = CurveFiPool(
            name=pool_meta["name"],
            type=PoolType.curvefi,
            tokens=pool_meta["tokens"],
            swap_type=pool_meta["swap_type"],
            pool_address=pool_meta["addresses"]["pool"],
        )

        return pool                