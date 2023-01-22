import asyncio
from decimal import Decimal
import os
import sys
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm

from warren.core.create_database import create_database
from warren.core.create_service import create_service
from warren.core.create_token_pair import create_token_pair
from warren.core.setup_wizard import SetupWizard
from warren.models.option import OptionDto
from warren.models.order import OrderDto, OrderStatus, OrderType
from warren.models.token_pair import TokenPair
from warren.tokens.dai import Dai
from warren.tokens.wbtc import WBtc
from warren.tokens.weth9 import WEth9
from warren.uniswap.v3.router import uniswap_v3_router_address
from warren.utils.format_exception import format_exception
from warren.utils.logger import logger
from warren.utils.print_order_table import print_order_table
from warren.utils.runner import Runner
from warren.utils.to_human import to_human
from warren.utils.to_wei import to_wei

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
    console.print("You will be asked to define passphare to your wallet. It's optional but strongly recommended.\n")
    console.print("Write down your passphrase. If you lose it you will no be able to access your funds.\n")
    console.print(
        "YOU ARE USING THIS APPLICATION AT YOUR OWN RISK! THIS APLLICATION HAS **NO WARRANTY** AND IT MIGHT NOT WORK CORRECTLY. YOU TAKE ALL RESPONSIBILITY FOR POSSIBLE LOSSES!\n",
        style="red bold",
    )

    have_read = Confirm.ask("I understand all information written above", show_default=True, default=False)
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
        console.print("Unfortunately, you cannot use Warren The Cryptobot without agreeing to all conditions.\n")
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
        passphrase = Prompt.ask("Enter passphrase (empty for no passphrase)", password=True)
        repeat_passphrase = Prompt.ask("Enter same passphrase again", password=True)

        if passphrase != repeat_passphrase:
            passphrase = None

    # Create database and save configs
    option_list = [OptionDto(option_name="eth_api_url", option_value=eth_api_url)]
    SetupWizard.create_database_in_config_dir(option_list=option_list, config_path=config_path)

    # Generate wallet and save configs
    encrypted_wallet = SetupWizard.generate_new_wallet(eth_api_url)
    SetupWizard.create_geth_file_in_config_dir(encrypted_wallet=encrypted_wallet, config_path=config_path)

    # Success!
    console.print(f"Your wallet credentials has been saved in {config_path}\n")
    console.print(f"Your wallet address is [green]0x{SetupWizard.get_wallet_address_from_config(config_path)}[/green]\n")


@main_app.command()
def start(
    config_dir: str = typer.Option(SetupWizard.default_config_path(), help="Path to the config directory."),
    seek_interval: int = typer.Option(12, help="Block seeking interval."),
):
    async def main():
        console: Console = Console()

        incorrect_config_dir = SetupWizard.verify_config_path(config_path=config_dir) == False
        if incorrect_config_dir:
            console.print("It seems like the config path does not exist. Did you run the setup script?")
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
def wrap_ether(config_dir: str = typer.Option(SetupWizard.default_config_path(), help="Path to the config directory.")):
    async def main():
        console: Console = Console()

        incorrect_config_dir = SetupWizard.verify_config_path(config_path=config_dir) == False
        if incorrect_config_dir:
            console.print("It seems like the config path does not exist. Did you run the setup script?")
            sys.exit(1)

        passphrase = Prompt.ask("Enter passphrase")
        service = create_service(config_path=config_dir, passphrase=passphrase)

        weth9 = WEth9(web3=service.web3, transaction_service=service.transaction_service)

        current_balance = service.web3.eth.get_balance(service.web3.eth.default_account)
        console.print(f"Before ETH balance: {to_human(current_balance, decimals=WEth9.decimals())} ETH")
        weth9_balance = weth9.balance_of(service.web3.eth.default_account)
        console.print(f"Before WETH9 balance: {to_human(weth9_balance, decimals=WEth9.decimals())} WETH9")

        amount_in = int(Prompt.ask("Enter amount to wrap (ETH)"))
        wei_amount_in = to_wei(amount_in, decimals=WEth9.decimals())
        await weth9.deposit(amount_in=wei_amount_in)
        console.print(f"Wrapped {to_human(wei_amount_in, decimals=WEth9.decimals())} ETH into WETH9")

        current_balance = service.web3.eth.get_balance(service.web3.eth.default_account)
        console.print(f"After ETH balance: {to_human(current_balance, decimals=WEth9.decimals())} ETH")
        weth9_balance = weth9.balance_of(service.web3.eth.default_account)
        console.print(f"After WETH9 balance: {to_human(weth9_balance, decimals=WEth9.decimals())} WETH9")

    asyncio.run(main())


# TODO(mateu.sh): use loop
# TODO(mateu.sh): use table to print results - it will look better
@main_app.command()
def balances(
    config_dir: str = typer.Option(SetupWizard.default_config_path(), help="Path to the config directory."),
):
    console: Console = Console()

    incorrect_config_dir = SetupWizard.verify_config_path(config_path=config_dir) == False
    if incorrect_config_dir:
        console.print("It seems like the config path does not exist. Did you run the setup script?")
        sys.exit(1)

    service = create_service(config_dir)

    console.print("")
    console.print("Token balances:\n")
    console.print(f"  ETH: {to_human(service.web3.eth.get_balance(service.web3.eth.default_account), decimals=WEth9.decimals())}")
    weth9 = WEth9(web3=service.web3, transaction_service=service.transaction_service)
    console.print(f"WETH9: {to_human(weth9.balance_of(service.web3.eth.default_account), decimals=WEth9.decimals())}")
    dai = Dai(web3=service.web3, transaction_service=service.transaction_service)
    console.print(f"  DAI: {to_human(dai.balance_of(service.web3.eth.default_account), decimals=Dai.decimals())}")
    wbtc = WBtc(web3=service.web3, transaction_service=service.transaction_service)
    console.print(f" WBTC: {to_human(wbtc.balance_of(service.web3.eth.default_account), decimals=WBtc.decimals())}")


# TODO(mateu.sh): support ETH wrapping
# TODO(mateu.sh): get rid of repeated code
@main_app.command()
def create_order(
    config_dir: str = typer.Option(SetupWizard.default_config_path(), help="Path to the config directory."),
):
    async def main():
        console: Console = Console()

        incorrect_config_dir = SetupWizard.verify_config_path(config_path=config_dir) == False
        if incorrect_config_dir:
            console.print("It seems like the config path does not exist. Did you run the setup script?")
            sys.exit(1)

        passphrase = Prompt.ask("Enter passphrase")
        order_book_v2 = create_service(config_path=config_dir, passphrase=passphrase)

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

        token_pair = create_token_pair(
            async_web3=order_book_v2.async_web3,
            web3=order_book_v2.web3,
            transaction_service=order_book_v2.transaction_service,
            token_pair=token_pairs[token_pair_idx],
        )

        token_in_balance = token_pair.token_in.balance_of(order_book_v2.web3.eth.default_account)
        console.print(f"Current price: {to_human(token_pair.quote(), decimals=token_pair.token_in.decimals())}")
        console.print(f"Balance: [green]{to_human(token_in_balance, decimals=token_pair.token_in.decimals())}[green]")

        if token_in_balance < token_pair.min_balance_to_transact:
            console.print(f"You don't have enough tokens")
            sys.exit(1)

        trigger_price = Decimal(Prompt.ask("Trigger price"))

        percent_of_tokens = Decimal(Prompt.ask("Percent of tokens to flip (excluding gas fees)", default=str(100)))
        await token_pair.token_in.approve(uniswap_v3_router_address, max_amount_in=token_in_balance)

        new_order = OrderDto(
            type=order_types[order_type_idx],
            token_pair=token_pairs[token_pair_idx],
            trigger_price=to_wei(trigger_price, decimals=token_pair.token_in.decimals()),
            percent=Decimal(percent_of_tokens / Decimal(100)),
            status=OrderStatus.active,
        )
        order_book_v2.database.create_order(order=new_order)

        console.print(f"The new order has been created.")

    asyncio.run(main())


@main_app.command()
def cancel_order(
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


@main_app.command()
def list_orders(
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
