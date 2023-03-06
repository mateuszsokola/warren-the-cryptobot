from typing import Any, Dict, List
from warren.models.network import Network
from warren.models.pools.base_pool import BasePool
from warren.models.pools.curvefi_pool import CurveFiPool
from warren.models.pools.pool_type import PoolType
from warren.utils.load_yaml import load_yaml


class PoolLoader:
    pools_by_type: Dict[PoolType, List[BasePool]] = {
        [PoolType.curvefi]: [],
    }

    def __init__(self):
        self.load_pool(filename="./metadata/pools/curvefi.yml")

    def load_pool(self, filename: str, network: Network = Network.Ethereum):
        file_content = load_yaml(filename)

        for pool_meta in file_content[network.value.lower()]:
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