import ast
from typing import Callable
from web3 import Web3
from web3.types import TxParams
from oracle.models.tx_fees import TxFees
from oracle.utils.logger import logger


class TransactionManager:
    def __init__(self, async_web3: Web3, web3: Web3):
        self.async_web3 = async_web3
        self.web3 = web3

    async def calculate_tx_fees(self, gas_limit: int = 200000):
        latest_block = await self.async_web3.eth.get_block("latest")
        max_priority_fee_per_gas = await self.async_web3.eth.max_priority_fee
        max_fee_per_gas = max_priority_fee_per_gas + (2 * latest_block["baseFeePerGas"])

        return TxFees(
            gas_limit=gas_limit,
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
        )

    async def send_transaction(self, tx_params: TxParams, success_cb: Callable = None, failure_cb: Callable = None):
        try:
            tx_hash = self.web3.eth.send_transaction(tx_params)

            tx_receipt = await self.async_web3.eth.wait_for_transaction_receipt(tx_hash)
            if tx_receipt.status == 1:
                if success_cb is not None:
                    success_cb(tx_receipt)
                else:
                    logger.info(f"Transaction #{tx_hash.hex()} succeeded.")
            else:
                if failure_cb is not None:
                    failure_cb(tx_receipt)
                else:
                    logger.error(f"Transaction #{tx_hash.hex()} failed. Increase gas limit.")

        except ValueError as value_error:
            error_json = ast.literal_eval(str(value_error))
            tx_receipt = await self.async_web3.eth.wait_for_transaction_receipt(error_json["data"]["txHash"])
            logger.error(
                f"Transaction #{tx_receipt.transactionHash.hex()} failed. Increase gas limit. Gas limit: {tx_params['gas']} gas used: {tx_receipt['gasUsed']} "
            )
            if failure_cb is not None:
                failure_cb(tx_receipt)

        except Exception as e:
            raise e
