import sqlite3
from decimal import Decimal
from typing import Callable, List, Tuple
from web3 import Web3
from web3.types import HexStr, LogReceipt
from oracle.models.flash_query.uniswap_v2_pair_reserves import UniswapV2PairReserves

from oracle.models.swapcat.sync_state import ProcessState
from oracle.models.swapcat.offer import SwapcatOffer
from oracle.models.uniswap.pair import UniswapV2PairDao, UniswapV2PairDto


class Store:
    def __init__(self, database_file: str):
        sqlite3.register_adapter(Decimal, lambda d: str(d))
        sqlite3.register_converter("DECTEXT", lambda d: Decimal(d.decode("ascii")))

        self.con = sqlite3.connect(database_file)
        self.cur = self.con.cursor()
        self.initial_block = 0

        self.init_db()

    def init_db(self):
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS swapcat_offers (
                id           INTEGER PRIMARY KEY,
                block_number INTEGER NOT NULL,
                token0 VARCHAR NOT NULL,
                token1 VARCHAR NOT NULL,
                recipient VARCHAR NOT NULL,
                amount VARCHAR NOT NULL,
                available_balance VARCHAR NOT NULL
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
                token1 VARCHAR NOT NULL,
                reserve0 VARCHAR NOT NULL,
                reserve1 VARCHAR NOT NULL,
                timestamp VARCHAR NOT NULL
            )
            """
        )
        self.con.commit()

    def create_sync_state_table(self, name: str):
        self.cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {name}_sync_state (
                id           INTEGER PRIMARY KEY DEFAULT 1,
                block_number INTEGER UNIQUE NOT NULL,
                last_idx INTEGER UNIQUE NOT NULL
            )
            """
        )
        self.con.commit()

    def last_sync_state(self, contract_name: str) -> ProcessState:
        select_query = f"SELECT block_number, last_idx FROM {contract_name}_sync_state"
        res: Tuple[int, int, int] = self.cur.execute(select_query).fetchone()
        if res is None:
            return ProcessState(block_number=0, last_idx=0)

        return ProcessState(block_number=res[0], last_idx=res[1])

    def set_last_sync_state(self, contract_name: str, block_number: int, last_idx: int):
        insert_query = f"INSERT OR REPLACE INTO {contract_name}_sync_state(id, block_number, last_idx) VALUES(?,?,?)"
        self.cur.execute(insert_query, [1, block_number, last_idx])

    def insert_or_replace_offer(self, offer: SwapcatOffer, should_commit: bool = False):
        self.cur.execute(
            """
            INSERT OR REPLACE INTO swapcat_offers (
                id,
                block_number,
                token0,
                token1,
                recipient,
                amount,
                available_balance
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                offer.id,
                offer.block_number,
                offer.token0,
                offer.token1,
                offer.recipient,
                str(offer.amount),
                str(offer.available_balance),
            ),
        )
        if should_commit:
            self.con.commit()

    def remove_offer(self, id: int, should_commit: bool = False):
        self.cur.execute(
            """
            DELETE FROM swapcat_offers WHERE id = ?
            """,
            [id],
        )
        if should_commit:
            self.con.commit()

    def insert_or_replace_pair(self, pair: UniswapV2PairDto):
        self.cur.execute(
            """
            INSERT OR REPLACE INTO uniswap_v2_pairs (
                type, 
                address, 
                token0, 
                token1, 
                reserve0, 
                reserve1, 
                timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (
                pair.type,
                pair.address,
                pair.token0,
                pair.token1,
                pair.reserve0,
                pair.reserve1,
                pair.timestamp,
            ),
        )
        self.con.commit()

    def list_swapcat_offers(self, asc: bool = True) -> List[SwapcatOffer]:
        select_clause = """
            SELECT
                id,
                block_number,
                token0,
                token1,
                recipient,
                amount,
                available_balance
            FROM swapcat_offers
        """
        order_clause = "ORDER BY id ASC" if asc == True else "ORDER BY id DESC"
        res = self.cur.execute(f"{select_clause} {order_clause}").fetchall()

        return [
            SwapcatOffer(
                id=id,
                block_number=block_number,
                token0=token0,
                token1=token1,
                recipient=recipient,
                amount=int(amount),
                available_balance=int(available_balance),
            )
            for (
                id,
                block_number,
                token0,
                token1,
                recipient,
                amount,
                available_balance,
            ) in res
        ]

    def list_uniswap_v2_pairs(self, asc: bool = True) -> List[UniswapV2PairDao]:
        select_clause = """
            SELECT
                id,
                type,
                address,
                token0,
                token1,
                reserve0,
                reserve1,
                timestamp
            FROM uniswap_v2_pairs
        """
        order_clause = "ORDER BY id ASC" if asc == True else "ORDER BY id DESC"
        res = self.cur.execute(f"{select_clause} {order_clause}").fetchall()

        return [
            UniswapV2PairDao(
                id=id,
                type=type,
                address=address,
                token0=token0,
                token1=token1,
                reserve0=reserve0,
                reserve1=reserve1,
                timestamp=timestamp,
            )
            for (
                id,
                type,
                address,
                token0,
                token1,
                reserve0,
                reserve1,
                timestamp,
            ) in res
        ]

    def list_uniswap_v2_pairs_by_tokens(self, token_a: str, token_b: str) -> List[UniswapV2PairDao]:
        select_clause = """
            SELECT
                id,
                type,
                address,
                token0,
                token1,
                reserve0,
                reserve1,
                timestamp
            FROM uniswap_v2_pairs
        """
        where_clause = """
        WHERE 
            (token0 = ? AND token1 = ?) OR 
            (token0 = ? AND token1 = ?) 
        """
        res = self.cur.execute(f"{select_clause} {where_clause}", [token_a, token_b, token_b, token_a]).fetchall()

        return [
            UniswapV2PairDao(
                id=id,
                type=type,
                address=address,
                token0=token0,
                token1=token1,
                reserve0=reserve0,
                reserve1=reserve1,
                timestamp=timestamp,
            )
            for (
                id,
                type,
                address,
                token0,
                token1,
                reserve0,
                reserve1,
                timestamp,
            ) in res
        ]

    def update_pair_reserves(self, pairs: List[UniswapV2PairReserves], should_commit: bool = False):
        for pair in pairs:
            self.cur.execute(
                f"UPDATE uniswap_v2_pairs SET reserve0 = ?, reserve1 = ?, timestamp = ? WHERE address = ?",
                [str(pair.reserve0), str(pair.reserve1), pair.timestamp, pair.address],
            )

        if should_commit:
            self.con.commit()


# All pairs matching to swapcat tokens
"""
SELECT * 
FROM uniswap_v2_pairs
WHERE
    reserve0 > 0 AND reserve1 > 0 AND
    (
        token0 IN (SELECT token0 FROM swapcat_offers) OR
        token1 IN (SELECT token0 FROM swapcat_offers)
    )
"""
