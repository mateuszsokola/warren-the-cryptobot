import asyncio
from decimal import Decimal
import sys
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from grid_trading.models.strategy_dto import StrategyDto
from grid_trading.models.strategy_status import StrategyStatus
from grid_trading.utils.print_strategy_table import print_strategy_table
from warren.core.create_database import create_database
from warren.core.create_service import create_service
from warren.core.setup_wizard import SetupWizard
from warren.managers.approval_manager import ApprovalManager
from warren.managers.price_manager import PriceManager
from warren.utils.choose_token_prompt import choose_token_prompt
from grid_trading.utils.token_prices_by_exchange_table import token_prices_by_route_table
from warren.utils.to_human import to_human

grid_trading_app = typer.Typer()


@grid_trading_app.command()
def create(
    config_dir: str = typer.Option(SetupWizard.default_config_path(), help="Path to the config directory."),
):
    async def main():
        console: Console = Console()

        incorrect_config_dir = SetupWizard.verify_config_path(config_path=config_dir) == False
        if incorrect_config_dir:
            console.print("It seems like the config path does not exist. Did you run the setup script?")
            sys.exit(1)

        passphrase = Prompt.ask("Enter passphrase")
        services = create_service(config_path=config_dir, passphrase=passphrase)

        token_routes = services.grid_trading.router.get_token_routes()
        token0 = choose_token_prompt(
            token_list=token_routes.keys(),
            token_service=services.grid_trading.token,
            console=console,
            prompt_message="Choose token0",
        )
        token1 = choose_token_prompt(
            token_list=token_routes[token0.name],
            token_service=services.grid_trading.token,
            console=console,
            prompt_message="Choose token1",
        )

        token0_balance = token0.balance_of(services.grid_trading.web3.eth.default_account)
        token1_balance = token1.balance_of(services.grid_trading.web3.eth.default_account)
        console.print(f"Balance: [green]{to_human(token0_balance, decimals=token0.decimals())} {token0.name}[green]")
        console.print(f"Balance: [green]{to_human(token1_balance, decimals=token1.decimals())} {token1.name}[green]")

        exchange_list = services.grid_trading.router.get_routes_by_token0_and_token1(
            token0=token0,
            token1=token1,
        )
        exchange_manager = PriceManager(route_list=exchange_list, token0=token0, token1=token1)
        table = token_prices_by_route_table(exchange_manager)
        console.print(table)

        grid_every_percent = Decimal(Prompt.ask("Grid every `n` percent"))

        percent_of_tokens = Decimal(Prompt.ask("Percent of tokens per flip (excluding gas fees)"))

        confirm = Confirm.ask("is it correct?")

        if confirm is False:
            console.print(f"Operation cancelled.")
            sys.exit(0)

        approval_manager = ApprovalManager(web3=services.web3, async_web3=services.async_web3)
        # TODO(mateu.sh): parametrize amount_in
        await approval_manager.approve_swaps(token_list=[token0, token1], route_list=exchange_list)

        new_order = StrategyDto(
            token0=token0,
            token1=token1,
            reference_price=exchange_manager.highest_price[2],
            last_tx_price=None,
            grid_every_percent=Decimal(grid_every_percent / Decimal(100)),
            percent_per_flip=Decimal(percent_of_tokens / Decimal(100)),
            status=StrategyStatus.active,
        )
        services.database.create_grid_trading_order(order=new_order)

        console.print(f"The new order has been created.")

    asyncio.run(main())


@grid_trading_app.command()
def cancel(
    config_dir: str = typer.Option(SetupWizard.default_config_path(), help="Path to the config directory."),
):
    console: Console = Console()

    incorrect_config_dir = SetupWizard.verify_config_path(config_path=config_dir) == False
    if incorrect_config_dir:
        console.print("It seems like the config path does not exist. Did you run the setup script?")
        sys.exit(1)

    service = create_database(config_dir)

    strategy_list = service.list_grid_trading_orders(status=StrategyStatus.active)
    print_strategy_table(strategy_list=strategy_list)

    strategy_id = int(Prompt.ask("Which strategy do you want to cancel? Provide the Order ID"))

    service.change_grid_trading_order_status(strategy_id, status=StrategyStatus.cancelled)

    console.print(f"The strategy #{strategy_id} has been cancelled.")


@grid_trading_app.command()
def list(
    config_dir: str = typer.Option(SetupWizard.default_config_path(), help="Path to the config directory."),
):
    console: Console = Console()

    incorrect_config_dir = SetupWizard.verify_config_path(config_path=config_dir) == False
    if incorrect_config_dir:
        console.print("It seems like the config path does not exist. Did you run the setup script?")
        sys.exit(1)

    service = create_database(config_dir)

    order_list = service.list_grid_trading_orders(status=None)
    print_strategy_table(strategy_list=order_list)
