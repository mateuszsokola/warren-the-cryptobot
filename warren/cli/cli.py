import asyncio
from decimal import Decimal
import os
import sys
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm

from warren.core.create_database import create_database
from warren.core.create_service import create_service
from warren.core.setup_wizard import SetupWizard
from warren.models.option import OptionDto
from warren.models.order import OrderDto, OrderStatus, OrderType
from warren.models.token_pair import TokenPair
from warren.tokens.dai import Dai
from warren.tokens.weth9 import WEth9
from warren.uniswap.v3.router import uniswap_v3_router_address
from warren.utils.format_exception import format_exception
from warren.utils.logger import logger
from warren.utils.print_order_table import print_order_table
from warren.utils.runner import Runner

main_app = typer.Typer()


@main_app.command()
def setup():
    console: Console = Console()

    # Show Terms of Service
    console.print("Welcome to Warren The Cryptobot!\n", style="bold")
    console.print(
        "Before we start you need to understand risks related to using [bold]Warren The Cryptobot[/bold]. This application will execute [italic]the real[/italic] transactions in your favor. [bold]Involving the real funds that have the real value![bold]\n"
    )
    console.print(
        "This installer will create a new wallet which will be used to interact with blockchains including but not limited to approving transactions, depositing coins and tokens, sending transactions etc. You should backup generated files in a secured place.\n"
    )
    console.print("Never share those files with anyone. Never.\n", style="bold")
    console.print(
        "You will be asked to define passphare to your wallet. It's optional but strongly recommended.\n"
    )
    console.print(
        "Write down your passphrase. If you lose it you will no be able to access your funds.\n"
    )
    console.print(
        "YOU ARE USING THIS APPLICATION AT YOUR OWN RISK! THIS APLLICATION HAS **NO WARRANTY** AND IT MIGHT NOT WORK CORRECTLY. YOU TAKE ALL RESPONSIBILITY FOR POSSIBLE LOSSES!\n",
        style="red bold",
    )

    have_read = Confirm.ask(
        "I understand all information written above", show_default=True, default=False
    )
    understand_risk = Confirm.ask(
        "I understand [bold]I can lose all my funds[/bold] by using this application",
        show_default=True,
        default=False,
    )
    taking_risk = Confirm.ask(
        "I understand this application comes with [bold]no warranty[/bold] and it [bold]might not work properly[/bold]. I take all responsibility for losses caused by this application.",
        show_default=True,
        default=False,
    )

    console.print("")

    if have_read == False or understand_risk == False or taking_risk == False:
        console.print(
            "Unfortunately, you cannot use Warren The Cryptobot without agreeing to all conditions.\n"
        )
        sys.exit(1)

    # Verify application dir
    default_config_path = SetupWizard.default_config_path()
    config_path = Prompt.ask(
        f"Enter file in which to save the wallet credentials",
        default=default_config_path,
        show_default=True,
    )
    if os.path.exists(config_path):
        console.print(f"{config_path} already exists.")
        should_override = Confirm.ask("Override?", show_default=True, default=False)
        if should_override == False:
            sys.exit(1)

    # Establish Ethereum API
    eth_api_url = None
    while eth_api_url is None:
        eth_api_url = Prompt.ask("Provide Ethereum API url")

        if SetupWizard.verify_ethereum_api(eth_api_url):
            console.print(f"Established connection to the Ethereum API\n")
        else:
            console.print("Ethereum API is not working. Try again.\n")
            eth_api_url = None

    # Define passphrase
    passphrase = None
    while passphrase is None:
        passphrase = Prompt.ask(
            "Enter passphrase (empty for no passphrase)", password=True
        )
        repeat_passphrase = Prompt.ask("Enter same passphrase again", password=True)

        if passphrase != repeat_passphrase:
            passphrase = None

    # Create database and save configs
    option_list = [OptionDto(option_name="eth_api_url", option_value=eth_api_url)]
    SetupWizard.create_database_in_config_dir(
        option_list=option_list, config_path=config_path
    )

    # Generate wallet and save configs
    encrypted_wallet = SetupWizard.generate_new_wallet(eth_api_url)
    SetupWizard.create_geth_file_in_config_dir(
        encrypted_wallet=encrypted_wallet, config_path=config_path
    )

    # Success!
    console.print(f"Your wallet credentials has been saved in {config_path}")


@main_app.command()
def start(
    config_dir: str = typer.Option(
        SetupWizard.default_config_path(), help="Path to the config directory."
    ),
    seek_interval: int = typer.Option(12, help="Block seeking interval."),
):
    async def main():
        console: Console = Console()

        incorrect_config_dir = (
            SetupWizard.verify_config_path(config_path=config_dir) == False
        )
        if incorrect_config_dir:
            console.print(
                "It seems like the config path does not exist. Did you run the setup script?"
            )
            sys.exit(1)

        passphrase = Prompt.ask("Enter passphrase")

        order_book_v2 = create_service(config_path=config_dir, passphrase=passphrase)
        runner = Runner.getInstance()

        try:
            await asyncio.gather(
                runner.with_loop(
                    order_book_v2.seek_for_opportunities,
                    interval=seek_interval,
                    stop_on_exception=False,
                ),
            )
            logger.info(f"Warren is shutting down now")
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.error(f"[MAIN_THREAD]: {format_exception()}")
            runner.graceful_shutdown()
            sys.exit(1)

    asyncio.run(main())

@main_app.command()
def wrap_ether_and_approve_uniswap_v3_router(
    config_dir: str = typer.Option(
        SetupWizard.default_config_path(), help="Path to the config directory."
    )    
):
    async def main():
        console: Console = Console()

        incorrect_config_dir = (
            SetupWizard.verify_config_path(config_path=config_dir) == False
        )
        if incorrect_config_dir:
            console.print(
                "It seems like the config path does not exist. Did you run the setup script?"
            )
            sys.exit(1)

        service = create_service(config_dir)

        weth9 = WEth9(web3=service.web3, transaction_service=service.transaction_service)

        current_balance = service.web3.eth.get_balance(service.web3.eth.default_account)
        console.print(f"Before ETH balance: {current_balance} wei")
        weth9_balance = weth9.balance_of(service.web3.eth.default_account)
        console.print(f"Before WETH9 balance: {weth9_balance} wei")

        amount_in = int(Prompt.ask("Enter amount to wrap"))
        tx_hash = await weth9.deposit(amount_in=amount_in)
        console.print(f"Wrapped {amount_in} wei into WETH9 wei", tx_hash)

        tx_hash = await weth9.approve(
            uniswap_v3_router_address, max_amount_in=amount_in
        )
        console.print(f"Allowed Uniswap v3 Router to execute transactions \n", tx_hash)

        current_balance = service.web3.eth.get_balance(service.web3.eth.default_account)
        console.print(f"After ETH balance: {current_balance} wei")
        weth9_balance = weth9.balance_of(service.web3.eth.default_account)
        console.print(f"After WETH9 balance: {weth9_balance} wei")

    asyncio.run(main())    


@main_app.command()
def wallet_balance(
    config_dir: str = typer.Option(
        SetupWizard.default_config_path(), help="Path to the config directory."
    ),
):
    console: Console = Console()

    incorrect_config_dir = (
        SetupWizard.verify_config_path(config_path=config_dir) == False
    )
    if incorrect_config_dir:
        console.print(
            "It seems like the config path does not exist. Did you run the setup script?"
        )
        sys.exit(1)

    service = create_service(config_dir)

    console.print("")
    console.print("Token balances:\n")
    console.print(
        f"  ETH: {service.web3.eth.get_balance(service.web3.eth.default_account)} wei"
    )
    weth9 = WEth9(web3=service.web3, transaction_service=service.transaction_service)
    console.print(
        f"WETH9: {weth9.balance_of(service.web3.eth.default_account)} wei"
    )
    dai = Dai(web3=service.web3, transaction_service=service.transaction_service)
    console.print(
        f"  DAI: {dai.balance_of(service.web3.eth.default_account)}"
    )


# TODO(mateu.sh): support ETH wrapping
# TODO(mateu.sh): get rid of repeated code
# TODO(mateu.sh): fetch price real time
# TODO(mateu.sh): get token decimals from classes
# TODO(mateu.sh): generalize tokens
@main_app.command()
def create_order(
    config_dir: str = typer.Option(
        SetupWizard.default_config_path(), help="Path to the config directory."
    ),
):
    console: Console = Console()

    incorrect_config_dir = (
        SetupWizard.verify_config_path(config_path=config_dir) == False
    )
    if incorrect_config_dir:
        console.print(
            "It seems like the config path does not exist. Did you run the setup script?"
        )
        sys.exit(1)

    service = create_database(config_dir)

    order_types = []
    choices = []
    for idx, order_type_idx in enumerate(OrderType):
        console.print(f"{idx}) {order_type_idx.value}")
        order_types.append(order_type_idx)
        choices.append(str(idx))

    order_type_idx = int(Prompt.ask("Choose order type", choices=choices))

    token_pairs = []
    choices = []
    for idx, token_pair_idx in enumerate(TokenPair):
        console.print(f"{idx}) {token_pair_idx.value}")
        token_pairs.append(token_pair_idx)
        choices.append(str(idx))

    token_pair_idx = int(Prompt.ask("Choose token pair", choices=choices))

    trigger_price = Decimal(Prompt.ask("Trigger price (DAI)")) * Decimal(10**18)

    percent_of_tokens = Decimal(
        Prompt.ask("Percent of tokens to flip (excluding gas fees)", default=str(100))
    )

    new_order = OrderDto(
        type=order_types[order_type_idx],
        token_pair=token_pairs[token_pair_idx],
        trigger_price=int(trigger_price),
        percent=Decimal(percent_of_tokens / Decimal(100)),
        status=OrderStatus.active,
    )
    service.create_order(order=new_order)

    console.print(f"The new order has been created.")


@main_app.command()
def cancel_order(
    config_dir: str = typer.Option(
        SetupWizard.default_config_path(), help="Path to the config directory."
    ),
):
    console: Console = Console()

    incorrect_config_dir = (
        SetupWizard.verify_config_path(config_path=config_dir) == False
    )
    if incorrect_config_dir:
        console.print(
            "It seems like the config path does not exist. Did you run the setup script?"
        )
        sys.exit(1)

    service = create_database(config_dir)

    order_list = service.list_orders(status=OrderStatus.active)
    print_order_table(order_list=order_list)

    order_id = int(
        Prompt.ask("Which order do you want to cancel? Provide the Order ID")
    )

    service.change_order_status(order_id, status=OrderStatus.cancelled)

    console.print(f"The order #{order_id} has been cancelled.")


@main_app.command()
def list_orders(
    config_dir: str = typer.Option(
        SetupWizard.default_config_path(), help="Path to the config directory."
    ),
):
    console: Console = Console()

    incorrect_config_dir = (
        SetupWizard.verify_config_path(config_path=config_dir) == False
    )
    if incorrect_config_dir:
        console.print(
            "It seems like the config path does not exist. Did you run the setup script?"
        )
        sys.exit(1)

    service = create_database(config_dir)

    order_list = service.list_orders(status=None)
    print_order_table(order_list=order_list)
