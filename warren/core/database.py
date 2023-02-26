import sqlite3
from decimal import Decimal
from typing import Callable, List
from explorer.models.pair import PairDto
from grid_trading.models.strategy_dao import BaseStrategyDao
from grid_trading.models.strategy_dto import StrategyDto
from grid_trading.models.strategy_status import StrategyStatus
from grid_trading.utils.create_strategy_dao import create_base_strategy_dao
from order_book.models.order_dto import OrderDto
from order_book.models.order_dao import BaseOrderDao
from order_book.models.order_status import OrderStatus
from order_book.utils.create_order_dao import create_base_order_dao
from warren.models.option import OptionDao, OptionDto
from warren.models.option_name import OptionName


class Database:
    def __init__(self, database_file: str):
        sqlite3.register_adapter(Decimal, lambda d: str(d))
        sqlite3.register_converter("DECTEXT", lambda d: Decimal(d.decode("ascii")))

        self.con = sqlite3.connect(database_file)
        self.cur = self.con.cursor()

        self.init_db()

    def init_db(self):
        self.cur.execute(
            """
                CREATE TABLE IF NOT EXISTS warren_options (
                    option_name VARCHAR PRIMARY KEY,
                    option_value VARCHAR NOT NULL
                )
            """
        )

        self.cur.execute(
            """
                CREATE TABLE IF NOT EXISTS order_book_v2 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type VARCHAR NOT NULL,
                    token0 VARCHAR NOT NULL,
                    token1 VARCHAR NOT NULL,
                    trigger_price VARCHAR NOT NULL,
                    percent VARCHAR NOT NULL,
                    status VARCHAR NOT NULL
                )
            """
        )

        self.cur.execute(
            """
                CREATE TABLE IF NOT EXISTS grid_trading_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token0 VARCHAR NOT NULL,
                    token1 VARCHAR NOT NULL,
                    reference_price VARCHAR NOT NULL,
                    last_tx_price VARCHAR DEFAULT NULL,
                    grid_every_percent VARCHAR NOT NULL,
                    percent_per_flip VARCHAR NOT NULL,
                    status VARCHAR NOT NULL
                )
            """
        )

        self.cur.execute(
            """
                CREATE TABLE IF NOT EXISTS uniswap_v2_pairs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type VARCHAR NOT NULL,
                    address VARCHAR NOT NULL,
                    token0 VARCHAR NOT NULL,
                    token1 VARCHAR NOT NULL
                )
            """
        )

    def insert_or_replace_pair(self, pair: PairDto):
        self.cur.execute(
            "INSERT OR REPLACE INTO uniswap_v2_pairs (type, address, token0, token1) VALUES(?, ?, ?, ?);",
            (
                pair.type,
                pair.address,
                pair.token0,
                pair.token1,
            ),
        )
        self.con.commit()

    def insert_or_replace_option(self, option: OptionDto):
        self.cur.execute(
            "INSERT OR REPLACE INTO warren_options (option_name, option_value) VALUES(?, ?);",
            (
                option.option_name.value,
                option.option_value,
            ),
        )
        self.con.commit()

    def create_order(self, order: OrderDto):
        self.cur.execute(
            """
                INSERT INTO order_book_v2
                (type, token0, token1, trigger_price, percent, status)
                VALUES(?, ?, ?, ?, ?, ?);
            """,
            (
                order.type.name,
                order.token0.name,
                order.token1.name,
                str(order.trigger_price),
                order.percent,
                order.status.name,
            ),
        )
        self.con.commit()

    def change_order_status(self, id: int, status: OrderStatus = OrderStatus.cancelled):
        update_query = "UPDATE order_book_v2 SET status = ? WHERE id = ?"
        self.cur.execute(
            update_query,
            [status.name, id],
        )
        self.con.commit()

    def list_options(self) -> List[OptionDao]:
        select_query = "SELECT option_name, option_value FROM warren_options"
        res = self.cur.execute(f"{select_query}").fetchall()

        return [OptionDao(option_name=OptionName[option_name], option_value=option_value) for (option_name, option_value) in res]

    def list_orders(self, func: Callable = create_base_order_dao, status: OrderStatus | None = None) -> List[BaseOrderDao]:
        select_query = """
            SELECT 
            id, type, token0, token1, trigger_price, percent, status
            FROM order_book_v2
        """
        if status is None:
            res = self.cur.execute(f"{select_query}").fetchall()
        else:
            res = self.cur.execute(f"{select_query} WHERE status = ?", [status.name]).fetchall()

        return [func(order) for order in res]

    def list_grid_trading_orders(
        self, func: Callable = create_base_strategy_dao, status: StrategyStatus | None = None
    ) -> List[BaseStrategyDao]:
        select_query = """
            SELECT 
            id, token0, token1, reference_price, last_tx_price, grid_every_percent, percent_per_flip, status
            FROM grid_trading_orders
        """
        if status is None:
            res = self.cur.execute(f"{select_query}").fetchall()
        else:
            res = self.cur.execute(f"{select_query} WHERE status = ?", [status.name]).fetchall()

        return [func(order) for order in res]

    def create_grid_trading_order(self, order: StrategyDto):
        self.cur.execute(
            """
                INSERT INTO grid_trading_orders
                (token0, token1, reference_price, last_tx_price, grid_every_percent, percent_per_flip, status)
                VALUES(?, ?, ?, ?, ?, ?, ?);
            """,
            (
                order.token0.name,
                order.token1.name,
                str(order.reference_price),
                str(order.last_tx_price),
                str(order.grid_every_percent),
                str(order.percent_per_flip),
                order.status.name,
            ),
        )
        self.con.commit()

    def change_grid_trading_order_last_tx_price(self, id: int, last_tx_price: int):
        update_query = "UPDATE grid_trading_orders SET last_tx_price = ? WHERE id = ?"
        self.cur.execute(
            update_query,
            [str(last_tx_price), id],
        )
        self.con.commit()

    def change_grid_trading_order_status(self, id: int, status: StrategyStatus = StrategyStatus.cancelled):
        update_query = "UPDATE grid_trading_orders SET status = ? WHERE id = ?"
        self.cur.execute(
            update_query,
            [status.name, id],
        )
        self.con.commit()
