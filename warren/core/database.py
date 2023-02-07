import sqlite3
from decimal import Decimal
from typing import List
from web3 import Web3
from warren.core.create_token import create_token
from warren.models.option import OptionDto
from warren.models.order import OrderDao, OrderDto, OrderStatus, OrderType


def order_dao_factory(web3: Web3, order: tuple):
    (id, order_type, token0, token1, trigger_price, percent, status) = order
    return OrderDao(
        id=id,
        type=OrderType[order_type],
        token0=create_token(web3=web3, name=token0),
        token1=create_token(web3=web3, name=token1),
        trigger_price=int(trigger_price),
        percent=Decimal(percent),
        status=OrderStatus[status],
    )


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
                CREATE TABLE IF NOT EXISTS order_book (
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
                INSERT INTO order_book
                (type, token0, token1, trigger_price, percent, status)
                VALUES(?, ?, ?, ?, ?);
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
        update_query = "UPDATE order_book SET status = ? WHERE id = ?"
        self.cur.execute(
            update_query,
            [status.name, id],
        )
        self.con.commit()

    def list_options(self) -> List[OptionDto]:
        select_query = "SELECT id, option_name, option_value FROM warren_options"
        res = self.cur.execute(f"{select_query}").fetchall()

        return [OptionDto(id=id, option_name=option_name, option_value=option_value) for (id, option_name, option_value) in res]

    def list_orders(self, web3: Web3, status: OrderStatus | None = None, func=order_dao_factory) -> List[OrderDao]:
        select_query = """
            SELECT 
            id, type, token0, token1, trigger_price, percent, status
            FROM order_book
        """
        if status is None:
            res = self.cur.execute(f"{select_query}").fetchall()
        else:
            res = self.cur.execute(f"{select_query} WHERE status = ?", [status.name]).fetchall()

        return [func(web3, order) for order in res]
