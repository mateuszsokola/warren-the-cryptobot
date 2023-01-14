from decimal import Decimal
from typing import List
from rich.console import Console
from rich.table import Table
from warren.models.order import OrderDao

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
            f"{str(Decimal(order.trigger_price) / Decimal(10 ** 18))} DAI",
            f"{int(order.percent * 100)} %",
            order.status.value,
        )

    console = Console()
    console.print(table)
