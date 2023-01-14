from pydantic import BaseModel


class OptionDao(BaseModel):
    id: int
    option_name: str
    option_value: str


class OptionDto(BaseModel):
    id: int | None = None
    option_name: str
    option_value: str
