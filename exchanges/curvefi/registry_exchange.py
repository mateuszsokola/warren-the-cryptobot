from web3 import Web3
from exchanges.curvefi.models.exchange_multiple import ExchangeMultiple
from exchanges.curvefi.models.get_exchange_multiple_amount_params import GetExchangeMultipleAmountParams

from warren.utils.load_contract_abi import load_contract_abi


DEFAULT_POOL_ADDRESSES = [
    "0x0000000000000000000000000000000000000000",
    "0x0000000000000000000000000000000000000000",
    "0x0000000000000000000000000000000000000000",
    "0x0000000000000000000000000000000000000000",
]


class CurveRegistryExchange:
    def __init__(self, web3: Web3, address: str):
        self.web3 = web3

        self.address = address
        self.contract = web3.eth.contract(
            address=address,
            abi=load_contract_abi("ICurvefiRegistryExchange.json", "artifacts/exchanges/curvefi"),
        )

    """
    @link https://github.com/curvefi/curve-pool-registry/blob/0bdb116024ccacda39295bb3949c3e6dd0a8e2d9/contracts/Swaps.vy#L872
    """

    def get_exchange_multiple_amount(
        self,
        params: GetExchangeMultipleAmountParams,
    ) -> int:
        amount_out = self.contract.functions.get_exchange_multiple_amount(params.route, params.swap_params, params.amount_in).call()

        return amount_out

    """
    @link https://github.com/curvefi/curve-pool-registry/blob/0bdb116024ccacda39295bb3949c3e6dd0a8e2d9/contracts/Swaps.vy#L872
    """

    def exchange_multiple(
        self,
        params: ExchangeMultiple,
        gas_limit: int,
        max_priority_fee_per_gas: int,
        max_fee_per_gas: int,
    ):
        tx = self.contract.functions.exchange_multiple(
            params.route,
            params.swap_params,
            params.amount_in,
            params.min_amount_out,
            DEFAULT_POOL_ADDRESSES,
        ).build_transaction(
            {
                "type": 2,
                "gas": gas_limit,
                "maxPriorityFeePerGas": max_priority_fee_per_gas,
                "maxFeePerGas": max_fee_per_gas,
                "value": 0,
            }
        )

        return tx
