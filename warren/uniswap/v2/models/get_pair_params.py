from pydantic import BaseModel


class GetPairParams(BaseModel):
    token_in: str
    token_out: str
