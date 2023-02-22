from rich.table import Table
from warren.managers.price_manager import PriceManager
from warren.utils.to_human import to_human

# TODO(mateu.sh): find better place for it
def token_prices_by_route_table(price_manager: PriceManager):
    table = Table(title="Token prices on decentralized exchanges")

    table.add_column("Exchange", style="magenta")
    table.add_column("Token0", justify="right", style="green")
    table.add_column("Token1", justify="right", style="green")

    for (exchange, token0_price, token1_price) in price_manager.retrieve_prices():
        table.add_row(
            exchange.name,
            f"{to_human(token0_price, decimals=price_manager.token0.decimals())} {price_manager.token0.name}",
            f"{to_human(token1_price, decimals=price_manager.token1.decimals())} {price_manager.token1.name}",
        )

    return table
