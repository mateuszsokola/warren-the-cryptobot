from web3 import Web3
from grid_trading.core.grid_trading_service import GridTradingService
from warren.core.database import Database
from warren.core.pool_loader import PoolLoader
from warren.core.router_v2 import RouterV2
from warren.core.token_service import TokenService
from warren.managers.config_manager import ConfigManager
from warren.models.base_model import BaseModel
from order_book.core.order_book_service import OrderBookService


class Service(BaseModel):
    async_web3: Web3
    web3: Web3
    config: ConfigManager
    database: Database
    token_service: TokenService
    pool_loader: PoolLoader
    router: RouterV2
    # order_book: OrderBookService
    # grid_trading: GridTradingService
