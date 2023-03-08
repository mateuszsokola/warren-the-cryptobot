import asyncio
from decimal import Decimal
import sys
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from fluffykitten.core.router import Router
from grid_trading.models.strategy_dto import StrategyDto
from grid_trading.models.strategy_status import StrategyStatus
from warren.core.create_service import create_service
from warren.core.setup_wizard import SetupWizard
from warren.managers.approval_manager import ApprovalManager
from warren.managers.price_manager import PriceManager
from warren.utils.choose_token_prompt import choose_token_prompt
from grid_trading.utils.token_prices_by_exchange_table import token_prices_by_route_table
from warren.utils.to_human import to_human

fluffykitten_app = typer.Typer()


@fluffykitten_app.command()
def list(
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

        router = Router(web3=services.web3, async_web3=services.async_web3)
        dai_amount_in = int(10000 * 10**18)

        for path in router.list_routes():
            max_amount_out = path.calculate_amount_out(dai_amount_in)
            console.print(f"{path.name} - {to_human(max_amount_out, decimals=18)} LINK")

        # paths = router.list_routes()
        # max_amount_out = paths[1].calculate_amount_out(dai_amount_in)
        # console.print(f"{paths[1].name} - {to_human(max_amount_out, decimals=18)} LINK")
        # dai_amount_out = paths[2].calculate_amount_out(max_amount_out)
        # console.print(f"{paths[2].name} - {to_human(dai_amount_out, decimals=18)} DAI")

    asyncio.run(main())
