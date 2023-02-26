from pydantic import BaseModel

from warren.models.option_name import OptionName


class OptionDao(BaseModel):
    option_name: OptionName
    option_value: str


class OptionDto(BaseModel):
    option_name: OptionName
    option_value: str
