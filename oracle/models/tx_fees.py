from pydantic import BaseModel


class TxFees(BaseModel):
    gas_limit: int
    max_fee_per_gas: int
    max_priority_fee_per_gas: int
