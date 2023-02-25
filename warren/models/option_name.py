from enum import Enum


class OptionName(str, Enum):
    eth_api_url = "eth_api_url"
    gas_limit = "gas_limit"
