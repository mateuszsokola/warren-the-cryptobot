import asyncio
from web3 import Web3

from oracle.core.store import Store
from oracle.models.token import Token
from oracle.utils.load_contract_abi import load_contract_abi
from oracle.utils.logger import logger


class TokenExplorer:
    def __init__(self, web3: Web3, store: Store):
        self.web3 = web3
        self.store = store

    def discover_token(self, address: str):
        contract = self.web3.eth.contract(
            Web3.toChecksumAddress(address),
            abi=load_contract_abi("WETH9.json", "artifacts/tokens"),
        )

        try:
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            token = Token(
                address=address,
                name=name,
                symbol=symbol,
                decimals=int(contract.functions.decimals().call()),
            )
            self.store.insert_or_replace_token(token)
            logger.info(f"New token {name} with symbol {symbol}")
        except: 
            logger.error(f"Couldn't process token with {address}")           
