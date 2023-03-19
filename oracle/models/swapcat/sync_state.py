from pydantic import BaseModel


class ProcessState(BaseModel):
    block_number: int
    last_idx: int
