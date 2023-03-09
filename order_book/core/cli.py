import asyncio
from decimal import Decimal
import sys
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from order_book.core.order_book_service import OrderBookService
from order_book.models.order_dto import OrderDto
from order_book.models.order_status import OrderStatus
from order_book.models.order_type import OrderType
from warren.core.create_database import create_database
from warren.core.create_service import create_service
from warren.core.setup_wizard import SetupWizard
from warren.managers.approval_manager import ApprovalManager
from order_book.utils.print_order_table import print_order_table
from warren.utils.choose_token_prompt import choose_token_prompt
from warren.utils.to_human import to_human
from warren.utils.to_wei import to_wei


order_book_app = typer.Typer()


# TODO(mateu.sh): support ETH wrapping
# TODO(mateu.sh): get rid of repeated code
@order_book_app.command()
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
        order_book = OrderBookService(
            async_web3=services.async_web3,
            web3=services.web3,
            database=services.database,
        )

        order_types = []
        choices = []
        for idx, order_type_idx in enumerate(OrderType):
            console.print(f"{idx}) {order_type_idx.value}")
            order_types.append(order_type_idx)
            choices.append(str(idx))

        order_type_idx = int(Prompt.ask("Choose order type", choices=choices))

        token0 = choose_token_prompt(
            token_list=order_book.router.get_all_tokens(),
            token_service=order_book.token,
            console=console,
            prompt_message="Choose token0",
        )

        token1 = choose_token_prompt(
            token_list=order_book.router.get_all_tokens_by_token0(token0),
            token_service=order_book.token,
            console=console,
            prompt_message="Choose token1",
        )

        routes = order_book.router.get_routes_by_token0_and_token1(
            token0=token0,
            token1=token1,
        )

        token0_balance = token0.balance_of(order_book.web3.eth.default_account)
        console.print(f"Balance: [green]{to_human(token0_balance, decimals=token0.decimals())} {token0.name}[green]")

        for route in routes:
            price = route.calculate_amount_out(token0=token0, token1=token1, amount_in=int(1 * 10 ** token0.decimals()))
            console.print(f"{route.name}: {to_human(price, decimals=token1.decimals())} {token1.name}")

        # TODO(mateu.sh): bring back `min_balance_to_transact`
        # if token_in_balance < token_pair.min_balance_to_transact:
        #     console.print(f"You don't have enough tokens")
        #     sys.exit(1)

        trigger_price = Decimal(Prompt.ask("Trigger price"))
        percent_of_tokens = Decimal(Prompt.ask("Percent of tokens to flip (excluding gas fees)", default=str(100)))

        confirm = Confirm.ask("is it correct?")

        if confirm is False:
            console.print(f"Operation cancelled.")
            sys.exit(0)

        approval_manager = ApprovalManager(web3=services.web3, async_web3=services.async_web3)
        await approval_manager.approve_swaps(token_list=[token0], route_list=routes, amount_in=token0_balance)

        new_order = OrderDto(
            type=order_types[order_type_idx],
            token0=token0,
            token1=token1,
            trigger_price=to_wei(trigger_price, decimals=token1.decimals()),
            percent=Decimal(percent_of_tokens / Decimal(100)),
            status=OrderStatus.active,
        )
        order_book.database.create_order(order=new_order)

        console.print(f"The new order has been created.")

    asyncio.run(main())


@order_book_app.command()
def cancel(
    config_dir: str = typer.Option(SetupWizard.default_config_path(), help="Path to the config directory."),
):
    console: Console = Console()

    incorrect_config_dir = SetupWizard.verify_config_path(config_path=config_dir) == False
    if incorrect_config_dir:
        console.print("It seems like the config path does not exist. Did you run the setup script?")
        sys.exit(1)

    service = create_database(config_dir)

    order_list = service.list_orders(status=OrderStatus.active)
    print_order_table(order_list=order_list)

    order_id = int(Prompt.ask("Which order do you want to cancel? Provide the Order ID"))

    service.change_order_status(order_id, status=OrderStatus.cancelled)

    console.print(f"The order #{order_id} has been cancelled.")


@order_book_app.command()
def list(
    config_dir: str = typer.Option(SetupWizard.default_config_path(), help="Path to the config directory."),
):
    console: Console = Console()

    incorrect_config_dir = SetupWizard.verify_config_path(config_path=config_dir) == False
    if incorrect_config_dir:
        console.print("It seems like the config path does not exist. Did you run the setup script?")
        sys.exit(1)

    service = create_database(config_dir)

    order_list = service.list_orders(status=None)
    print_order_table(order_list=order_list)
