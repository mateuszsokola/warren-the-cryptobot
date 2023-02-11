import asyncio
from decimal import Decimal
import os
import sys
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from warren.core.create_service import create_service
from warren.core.create_token import create_token
from warren.core.setup_wizard import SetupWizard
from warren.managers.exchange_manager import ExchangeManager
from warren.services.transaction_service import TransactionService
from warren.utils.choose_token_prompt import choose_token_prompt
from warren.utils.create_token_prices_by_exchange_table import create_token_prices_by_exchange_table
from warren.utils.logger import logger
from warren.utils.to_human import to_human
from warren.utils.to_wei import to_wei

degen_app = typer.Typer()


@degen_app.command()
def create_strategy(
    config_dir: str = typer.Option(SetupWizard.default_config_path(), help="Path to the config directory."),
):
    async def main():
        console: Console = Console()

        incorrect_config_dir = SetupWizard.verify_config_path(config_path=config_dir) == False
        if incorrect_config_dir:
            console.print("It seems like the config path does not exist. Did you run the setup script?")
            sys.exit(1)

        passphrase = Prompt.ask("Enter passphrase")
        # TODO(mateu.sh): it shouldn't create order book!
        order_book_v2 = create_service(config_path=config_dir, passphrase=passphrase)

        token_routes = order_book_v2.router.get_token_routes()
        token0 = choose_token_prompt(
            token_list=token_routes.keys(), token_service=order_book_v2.token, console=console, prompt_message="Choose token0"
        )
        token1 = choose_token_prompt(
            token_list=token_routes[token0.name], token_service=order_book_v2.token, console=console, prompt_message="Choose token1"
        )

        token0_balance = token0.balance_of(order_book_v2.web3.eth.default_account)
        token1_balance = token1.balance_of(order_book_v2.web3.eth.default_account)
        console.print(f"Balance: [green]{to_human(token0_balance, decimals=token0.decimals())} {token0.name}[green]")
        console.print(f"Balance: [green]{to_human(token1_balance, decimals=token1.decimals())} {token1.name}[green]")

        exchange_list = order_book_v2.router.get_token_pair_by_token0_and_token1(
            token0=token0,
            token1=token1,
        )
        exchange_manager = ExchangeManager(exchange_list=exchange_list, token0=token0, token1=token1)
        table = create_token_prices_by_exchange_table(exchange_manager)
        console.print(table)

        buy_trigger_price_decimal = Decimal(Prompt.ask("Price delta for buy orders"))
        buy_trigger_price = to_wei(amount=buy_trigger_price_decimal, decimals=token1.decimals())
        console.print(f"The system will buy tokens when price at any exchanges drops below {to_human(int(exchange_manager.lowest_price[2] - buy_trigger_price), decimals=token1.decimals())} {token1.name}")

        sell_trigger_price_decimal = Decimal(Prompt.ask("Price delta for sell orders"))
        sell_trigger_price = to_wei(amount=sell_trigger_price_decimal, decimals=token1.decimals())
        console.print(f"The system will sell tokens when price at any exchanges exceeds {to_human(int(exchange_manager.highest_price[2] + sell_trigger_price), decimals=token1.decimals())} {token1.name}")

        confirm = Confirm.ask("is it correct?")

    asyncio.run(main())
