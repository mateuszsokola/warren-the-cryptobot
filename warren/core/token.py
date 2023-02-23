from typing import Dict
from web3 import Web3

from tokens.base_token import BaseToken
from warren.core.create_token import create_token
from warren.models.network import Network
from warren.utils.load_yaml import load_yaml


class Token:
    _token_map: Dict[str, BaseToken] = {}

    def __init__(self, web3: Web3, async_web3: Web3, filename: str = "./tokens.yml"):
        self.async_web3 = async_web3
        self.web3 = web3

        self._token_map = self._load_tokens(filename=filename)

    def get_token_by_name(self, name: str) -> BaseToken:
        if self._token_map[name] is None:
            return None

        return self._token_map[name]

    def _load_tokens(self, filename: str, network: Network = Network.Ethereum):
        result: dict(str, BaseToken) = {}

        file_content = load_yaml(filename)
        # TODO(mateu.sh): add asserts to every record
        for meta in file_content["networks"][network.value.lower()]:
            name = meta["name"]

            result[name] = create_token(web3=self.web3, name=name, address=str(meta["address"]))

        return result
