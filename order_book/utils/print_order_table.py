from typing import List
from rich.console import Console
from rich.table import Table
from order_book.models.order_dao import BaseOrderDao
from tokens.utils.get_token_class_by_name import get_token_class_by_name
from warren.utils.to_human import to_human


def print_order_table(order_list: List[BaseOrderDao]):
    table = Table(title="Order book")

    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Token0", justify="right", style="green")
    table.add_column("Token1", justify="right", style="green")
    table.add_column("Trigger price", justify="right", style="green")
    table.add_column("Token amount [%]", justify="right", style="green")
    table.add_column("Status", justify="right", style="green")

    for order in order_list:
        TokenClass = get_token_class_by_name(order.token1)
        
        table.add_row(
            str(order.id),
            order.type.value,
            order.token0,
            order.token1,
            f"{to_human(order.trigger_price, decimals=TokenClass.decimals())} {order.token1}",
            f"{int(order.percent * 100)} %",
            order.status.value,
        )

    console = Console()
    console.print(table)
