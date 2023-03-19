from typing import Dict, Any, Tuple, List, Type, Union, Optional

from web3 import Web3
from web3.contract import Contract
from web3.types import LogReceipt, TxData


class BaseContractExplorer:
    def __init__(self, async_web3: Web3, contract: Union[Contract, Type[Contract]], name: str):
        """
        The ContractExplorer constructor.

        Args:
            contract_address: Address of deployed contract.
            store:            OracleStore
        """

        self.async_web3 = async_web3
        self.contract = contract
        self.name = name

    async def get_log_receipts_from_contract(
        self,
        from_block: int,
        to_block: Union[int, str] = "latest",
        use_contract_address: bool = True,
        topics: Optional[List[str]] = None,
    ) -> List[LogReceipt]:
        """
        Initializes and enqueues batch deposit log receipts
        to catch up with the latest block and then exits.

        Returns:
            A list of log receipts
        """
        print(
            {
                "fromBlock": from_block,
                "toBlock": to_block,
                "address": self.contract.address if use_contract_address else [],
                "topics": topics,
            }
        )
        return await self.async_web3.eth.get_logs(
            {
                "fromBlock": from_block,
                "toBlock": to_block,
                "address": self.contract.address if use_contract_address else [],
                "topics": topics,
            }
        )

    async def get_tx_and_decode_fn(
        self, log_receipt: LogReceipt, function_selector: str
    ) -> Optional[Tuple[Optional[Dict[str, Any]], TxData]]:
        tx_hash = log_receipt.transactionHash
        tx = await self.async_web3.eth.get_transaction(tx_hash)
        """
        Extract and process function from log receipt
        """
        if tx.input[2:10] == function_selector:
            decoded_fn = self.contract.decode_function_input(tx.input)[1]
            return decoded_fn, tx

        return None
