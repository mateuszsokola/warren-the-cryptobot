from typing import List
from rich.console import Console
from rich.table import Table
from grid_trading.models.strategy_dao import BaseStrategyDao
from tokens.dai import DAI
from warren.utils.to_human import to_human


def print_strategy_table(strategy_list: List[BaseStrategyDao]):
    table = Table(title="Order book")

    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Token0", justify="right", style="green")
    table.add_column("Token1", justify="right", style="green")
    table.add_column("Reference price", justify="right", style="green")
    table.add_column("Grid every [%]", justify="right", style="green")
    table.add_column("Tokens to flip [%]", justify="right", style="green")
    table.add_column("Status", justify="right", style="green")

    for strategy in strategy_list:
        table.add_row(
            str(strategy.id),
            strategy.token0,
            strategy.token1,
            # TODO(mateu.sh): use actual token name
            f"{to_human(strategy.reference_price, decimals=DAI.decimals())} DAI",
            # TODO(mateu.sh): use actual token name
            f"{to_human(strategy.last_tx_price, decimals=DAI.decimals())} DAI",
            f"{int(strategy.grid_every_percent * 100)} %",
            f"{int(strategy.percent_per_flip * 100)} %",
            strategy.status.value,
        )

    console = Console()
    console.print(table)
