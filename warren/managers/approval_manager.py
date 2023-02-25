import asyncio
import functools
from web3 import Web3
from web3.types import TxReceipt
from typing import List
from tokens.base_token import BaseToken
from warren.managers.transaction_manager import TransactionManager
from warren.routes.base_route import BaseRoute
from warren.routes.mooniswap_route import MooniswapRoute
from warren.routes.stableswap_3pool_route import StableSwap3poolRoute
from warren.routes.uniswap_v2 import UniswapV2Route
from warren.routes.uniswap_v3 import UniswapV3Route
from warren.utils.logger import logger


def success_callback(exchange_name: str, token_name: str, tx: TxReceipt):
    logger.info(f"TOKEN APPROVAL | Approved {exchange_name} for token {token_name}. TX #{tx.transactionHash.hex()}")


def failure_callback(exchange_name: str, token_name: str, tx: TxReceipt):
    logger.error(f"TOKEN APPROVAL | Failed to approve {exchange_name} for token {token_name}. TX #{tx.transactionHash.hex()}")


class ApprovalManager:
    def __init__(self, async_web3: Web3, web3: Web3):
        self.transaction_manager = TransactionManager(async_web3=async_web3, web3=web3)

    async def approve_swaps(
        self,
        token_list: List[BaseToken],
        route_list: List[BaseRoute],
        amount_in: int = int(10 * 10**18),
        gas_limit: int = 120000,
    ):
        fees = await self.transaction_manager.calculate_tx_fees(gas_limit=gas_limit)
        txs = []

        for token in token_list:
            for route in route_list:
                if isinstance(route, MooniswapRoute):
                    txs.append(
                        asyncio.create_task(
                            self.transaction_manager.send_transaction(
                                token.approve(
                                    route.pool.address,
                                    max_amount_in=amount_in,
                                    gas_limit=fees.gas_limit,
                                    max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
                                    max_fee_per_gas=fees.max_fee_per_gas,
                                ),
                                success_cb=functools.partial(success_callback, route.name, token.name),
                                failure_cb=functools.partial(failure_callback, route.name, token.name),
                            )
                        )
                    )
                elif isinstance(route, StableSwap3poolRoute):
                    txs.append(
                        asyncio.create_task(
                            self.transaction_manager.send_transaction(
                                token.approve(
                                    route.pool.address,
                                    max_amount_in=amount_in,
                                    gas_limit=fees.gas_limit,
                                    max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
                                    max_fee_per_gas=fees.max_fee_per_gas,
                                ),
                                success_cb=functools.partial(success_callback, route.name, token.name),
                                failure_cb=functools.partial(failure_callback, route.name, token.name),
                            )
                        )
                    )
                elif isinstance(route, UniswapV2Route):
                    txs.append(
                        asyncio.create_task(
                            self.transaction_manager.send_transaction(
                                token.approve(
                                    route.router.address,
                                    max_amount_in=amount_in,
                                    gas_limit=fees.gas_limit,
                                    max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
                                    max_fee_per_gas=fees.max_fee_per_gas,
                                ),
                                success_cb=functools.partial(success_callback, route.name, token.name),
                                failure_cb=functools.partial(failure_callback, route.name, token.name),
                            )
                        )
                    )
                elif isinstance(route, UniswapV3Route):
                    txs.append(
                        asyncio.create_task(
                            self.transaction_manager.send_transaction(
                                token.approve(
                                    route.router.address,
                                    max_amount_in=amount_in,
                                    gas_limit=fees.gas_limit,
                                    max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
                                    max_fee_per_gas=fees.max_fee_per_gas,
                                ),
                                success_cb=functools.partial(success_callback, route.name, token.name),
                                failure_cb=functools.partial(failure_callback, route.name, token.name),
                            )
                        )
                    )
                else:
                    logger.warn(f"TOKEN APPROVAL | Unsupported Route: {route.name}")

        return await asyncio.gather(*txs)
