import asyncio
import functools
from typing import List
from web3 import Web3
from web3.types import TxReceipt
from grid_trading.models.strategy_dao import StrategyDao
from grid_trading.models.strategy_status import StrategyStatus
from grid_trading.utils.create_grid import create_grid
from grid_trading.utils.create_strategy_dao import create_strategy_dao
from tokens.base_token import BaseToken
from warren.core.database import Database
from warren.core.token import Token
from warren.core.router import Router
from warren.managers.price_manager import PriceManager
from warren.utils.logger import logger
from warren.utils.to_human import to_human


class UniswapV2Explorer:
    def __init__(self, async_web3: Web3, web3: Web3, database: Database):
        self.async_web3 = async_web3
        self.web3 = web3
        self.database = database
        self.token = Token(
            async_web3=async_web3,
            web3=web3,
        )
