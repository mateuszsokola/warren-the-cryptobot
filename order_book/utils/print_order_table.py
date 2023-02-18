from typing import List
from rich.console import Console
from rich.table import Table
from order_book.models.order import OrderDao
from tokens.dai import DAI
from warren.utils.to_human import to_human

# TODO(mateu.sh): find better place for it
def print_order_table(order_list: List[OrderDao]):
    table = Table(title="Order book")

    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Token pair", justify="right", style="green")
    table.add_column("Trigger price", justify="right", style="green")
    table.add_column("Token amount [%]", justify="right", style="green")
    table.add_column("Status", justify="right", style="green")

    for order in order_list:
        table.add_row(
            str(order.id),
            order.type.value,
            order.token_pair.value,
            # TODO(mateu.sh): it suppose to display all decimals instead of cutting them once hit zeros
            f"{to_human(order.trigger_price, decimals=DAI.decimals())} DAI",
            f"{int(order.percent * 100)} %",
            order.status.value,
        )

    console = Console()
    console.print(table)
