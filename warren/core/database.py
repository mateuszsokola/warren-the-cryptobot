import sqlite3
from decimal import Decimal
from typing import Callable, List
from grid_trading.models.order import GridTradingOrderDao, GridTradingOrderDto, GridTradingOrderStatus
from warren.models.option import OptionDto
from order_book.models.order import OrderDao, OrderDto, OrderStatus


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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    option_name VARCHAR NOT NULL,
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

    def create_option(self, option: OptionDto):
        self.cur.execute(
            "INSERT INTO warren_options (option_name, option_value) VALUES(?, ?);",
            (
                option.option_name,
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

    def list_options(self) -> List[OptionDto]:
        select_query = "SELECT id, option_name, option_value FROM warren_options"
        res = self.cur.execute(f"{select_query}").fetchall()

        return [OptionDto(id=id, option_name=option_name, option_value=option_value) for (id, option_name, option_value) in res]

    def list_orders(self, func: Callable, status: OrderStatus | None = None) -> List[OrderDao]:
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

    def list_grid_trading_orders(self, func: Callable, status: GridTradingOrderStatus | None = None) -> List[GridTradingOrderDao]:
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

    def create_grid_trading_order(self, order: GridTradingOrderDto):
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
