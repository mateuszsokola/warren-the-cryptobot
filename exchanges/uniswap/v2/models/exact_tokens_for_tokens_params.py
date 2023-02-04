from pydantic import BaseModel


# TODO(mateu.sh): receiving wallet is missing
class ExactTokensForTokensParams(BaseModel):
    token_in: str
    token_out: str
    amount_in: int
    amount_out_minimum: int
    deadline: int
