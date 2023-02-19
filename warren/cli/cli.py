import asyncio
import os
import sys
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from tokens.weth9 import WETH9
from tokens.wxdai import WXDAI
from grid_trading.core.cli import grid_trading_app
from order_book.core.cli import order_book_app
from warren.core.create_service import create_service
from warren.core.setup_wizard import SetupWizard
from warren.models.option import OptionDto
from warren.services.transaction_service import TransactionService
from warren.utils.format_exception import format_exception
from warren.utils.logger import logger
from warren.utils.runner import Runner
from warren.utils.to_human import to_human
from warren.utils.to_wei import to_wei


main_app = typer.Typer()
main_app.add_typer(order_book_app, name="order-book")
main_app.add_typer(grid_trading_app, name="grid-trading")


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

        services = create_service(config_path=config_dir, passphrase=passphrase)
        runner = Runner.getInstance()

        try:
            await asyncio.gather(
                runner.with_loop(
                    services.order_book.find_opportunities,
                    interval=seek_interval,
                    stop_on_exception=False,
                ),
                runner.with_loop(
                    services.grid_trading.find_opportunities,
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
def wrap_native_token(config_dir: str = typer.Option(SetupWizard.default_config_path(), help="Path to the config directory.")):
    async def main():
        console: Console = Console()

        incorrect_config_dir = SetupWizard.verify_config_path(config_path=config_dir) == False
        if incorrect_config_dir:
            console.print("It seems like the config path does not exist. Did you run the setup script?")
            sys.exit(1)

        passphrase = Prompt.ask("Enter passphrase")
        services = create_service(config_path=config_dir, passphrase=passphrase)

        # TODO(mateu.sh): this shouldn't be hardcoded
        wrapped_native_token = WETH9(web3=services.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
        # wrapped_native_token = WXDAI(web3=services.web3, address="0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d")

        current_balance = services.web3.eth.get_balance(services.web3.eth.default_account)
        console.print(f"Before ETH balance: {to_human(current_balance, decimals=WETH9.decimals())} ETH")
        wrapped_balance = wrapped_native_token.balance_of(services.web3.eth.default_account)
        console.print(
            f"Before {wrapped_native_token.name} balance: {to_human(wrapped_balance, decimals=WETH9.decimals())} {wrapped_native_token.name}"
        )

        amount_in = int(Prompt.ask("Enter amount to wrap (ETH)"))
        wei_amount_in = to_wei(amount_in, decimals=WETH9.decimals())

        transaction_service = TransactionService(web3=services.web3, async_web3=services.async_web3)
        fees = await transaction_service.calculate_tx_fees(gas_limit=120000)

        await transaction_service.send_transaction(
            wrapped_native_token.deposit(
                amount_in=wei_amount_in,
                gas_limit=fees.gas_limit,
                max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
                max_fee_per_gas=fees.max_fee_per_gas,
            )
        )
        console.print(
            f"Wrapped {to_human(wei_amount_in, decimals=wrapped_native_token.decimals())} ETH into {wrapped_native_token.name}"
        )

        current_balance = services.web3.eth.get_balance(services.web3.eth.default_account)
        console.print(f"After ETH balance: {to_human(current_balance, decimals=WETH9.decimals())} ETH")
        wrapped_balance = wrapped_native_token.balance_of(services.web3.eth.default_account)
        console.print(
            f"After {wrapped_native_token.name} balance: {to_human(wrapped_balance, decimals=WETH9.decimals())} {wrapped_native_token.name}"
        )

    asyncio.run(main())


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

    services = create_service(config_dir)

    console.print("")
    console.print("Token balances:\n")

    # TODO(mateu.sh): it should use native token
    console.print(f"  ETH: {to_human(services.web3.eth.get_balance(services.web3.eth.default_account), decimals=WETH9.decimals())}")

    for token in services.order_book.token.get_all_tokens():
        console.print(f"{token.name}: {to_human(token.balance_of(services.web3.eth.default_account), decimals=token.decimals())}")
