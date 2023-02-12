import asyncio
from decimal import Decimal
import os
import sys
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from grid_trading.core.create_service import create_service
from grid_trading.models.order import GridTradingOrderDto, GridTradingOrderStatus
from warren.core.create_token import create_token
from warren.core.setup_wizard import SetupWizard
from warren.managers.exchange_manager import ExchangeManager
from warren.services.transaction_service import TransactionService
from warren.utils.choose_token_prompt import choose_token_prompt
from warren.utils.create_token_prices_by_exchange_table import create_token_prices_by_exchange_table
from warren.utils.logger import logger
from warren.utils.to_human import to_human
from warren.utils.to_wei import to_wei

grid_trading_app = typer.Typer()


@grid_trading_app.command()
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

        buy_delta_trigger_decimal = Decimal(Prompt.ask("Price delta for buy orders"))
        buy_delta_trigger = to_wei(amount=buy_delta_trigger_decimal, decimals=token1.decimals())
        console.print(
            f"SIMULATION FOR THE FIRST TX ONLY! Tokens will be bought when price on any exchange drops below {to_human(int(exchange_manager.lowest_price[2] - buy_delta_trigger), decimals=token1.decimals())} {token1.name}"
        )

        sell_delta_trigger_decimal = Decimal(Prompt.ask("Price delta for sell orders"))
        sell_delta_trigger = to_wei(amount=sell_delta_trigger_decimal, decimals=token1.decimals())
        console.print(
            f"SIMULATION FOR THE FIRST TX ONLY! Tokens will be sold when price on any exchange exceeds {to_human(int(exchange_manager.highest_price[2] + sell_delta_trigger), decimals=token1.decimals())} {token1.name}"
        )

        percent_of_tokens = Decimal(Prompt.ask("Percent of tokens per flip (excluding gas fees)"))

        confirm = Confirm.ask("is it correct?")

        if confirm is False:
            console.print(f"Operation cancelled.")
            sys.exit(0)

        new_order = GridTradingOrderDto(
            token0=token0,
            token1=token1,
            buy_delta_trigger=buy_delta_trigger,
            sell_delta_trigger=sell_delta_trigger,
            percent_per_flip=Decimal(percent_of_tokens / Decimal(100)),
            status=GridTradingOrderStatus.active,
        )
        order_book_v2.database.create_grid_trading_order(order=new_order)

        console.print(f"The new order has been created.")

        # 
        # TODO
        # ======
        # - [ ] - Persist strategy in database (maybe warren_options? - wrong i'd say) include current prices
        # - [ ] - Implement trading bot
        # - [ ] - Record trxs in database 
        # - [ ] - Move order book to separate CLI group
        # - [ ] - Allow tokens to execute trxs (all relevant routers)
        # - [ ] - Display warning if amount of tokens doens't allow to execute any trx



    asyncio.run(main())
