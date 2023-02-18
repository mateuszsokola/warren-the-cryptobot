from web3 import Web3
from grid_trading.services.grid_trading_service import GridTradingService
from warren.core.database import Database
from warren.models.base_model import BaseModel
from order_book.core.order_book_service import OrderBookService


class Service(BaseModel):
    async_web3: Web3
    web3: Web3
    database: Database
    order_book: OrderBookService
    grid_trading: GridTradingService
