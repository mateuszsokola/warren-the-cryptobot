import asyncio
import functools
from web3 import Web3
from web3.types import TxReceipt
from typing import List
from tokens.base_token import BaseToken
from warren.core.base_token_pair import BaseTokenPair
from warren.core.uniswap_v2_token_pair import UniswapV2TokenPair
from warren.core.uniswap_v3_token_pair import UniswapV3TokenPair
from warren.services.transaction_service import TransactionService
from warren.utils.logger import logger


def success_callback(exchange_name: str, token_name: str, tx: TxReceipt):
    logger.info(f"TOKEN APPROVAL | Approved {exchange_name} for token {token_name}. TX #{tx.transactionHash.hex()}")


def failure_callback(exchange_name: str, token_name: str, tx: TxReceipt):
    logger.error(f"TOKEN APPROVAL | Failed to approve {exchange_name} for token {token_name}. TX #{tx.transactionHash.hex()}")


class ApprovalManager:
    def __init__(self, async_web3: Web3, web3: Web3):
        self.transaction_manager = TransactionService(async_web3=async_web3, web3=web3)

    async def approve_swaps(
        self,
        token_list: List[BaseToken],
        exchange_list: List[BaseTokenPair],
        amount_in: int = int(10 * 10**18),
        gas_limit: int = 120000,
    ):
        fees = await self.transaction_manager.calculate_tx_fees(gas_limit=gas_limit)
        txs = []

        for token in token_list:
            for exchange in exchange_list:
                if isinstance(exchange, UniswapV2TokenPair):
                    txs.append(
                        asyncio.create_task(
                            self.transaction_manager.send_transaction(
                                token.approve(
                                    exchange.uniswap_v2_router.address,
                                    max_amount_in=amount_in,
                                    gas_limit=fees.gas_limit,
                                    max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
                                    max_fee_per_gas=fees.max_fee_per_gas,
                                ),
                                success_cb=functools.partial(success_callback, exchange.name, token.name),
                                failure_cb=functools.partial(failure_callback, exchange.name, token.name),
                            )
                        )
                    )
                elif isinstance(exchange, UniswapV3TokenPair):
                    txs.append(
                        asyncio.create_task(
                            self.transaction_manager.send_transaction(
                                token.approve(
                                    exchange.uniswap_v3_router.address,
                                    max_amount_in=amount_in,
                                    gas_limit=fees.gas_limit,
                                    max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
                                    max_fee_per_gas=fees.max_fee_per_gas,
                                ),
                                success_cb=functools.partial(success_callback, exchange.name, token.name),
                                failure_cb=functools.partial(failure_callback, exchange.name, token.name),
                            )
                        )
                    )
                else:
                    logger.warn(f"TOKEN APPROVAL | Unsupported TokenPair for Exchange `{exchange.name}")

        return await asyncio.gather(*txs)
