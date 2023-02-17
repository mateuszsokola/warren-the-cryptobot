import asyncio
from decimal import Decimal
import os
import sys
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from tokens.dai import DAI
from tokens.usdc import USDC
from tokens.wbtc import WBTC
from tokens.weth9 import WETH9
from grid_trading.core.cli import grid_trading_app
from warren.core.create_database import create_database
from warren.core.create_service import create_service
from warren.core.setup_wizard import SetupWizard
from warren.models.option import OptionDto
from warren.models.order import OrderDto, OrderStatus, OrderType
from warren.services.transaction_service import TransactionService
from warren.utils.format_exception import format_exception
from warren.utils.logger import logger
from warren.utils.print_order_table import print_order_table
from warren.utils.runner import Runner
from warren.utils.to_human import to_human
from warren.utils.to_wei import to_wei


main_app = typer.Typer()
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
                    services.order_book.seek_for_opportunities,
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
def wrap_ether(config_dir: str = typer.Option(SetupWizard.default_config_path(), help="Path to the config directory.")):
    async def main():
        console: Console = Console()

        incorrect_config_dir = SetupWizard.verify_config_path(config_path=config_dir) == False
        if incorrect_config_dir:
            console.print("It seems like the config path does not exist. Did you run the setup script?")
            sys.exit(1)

        passphrase = Prompt.ask("Enter passphrase")
        services = create_service(config_path=config_dir, passphrase=passphrase)

        # TODO(mateu.sh): this shouldn't be hardcoded
        weth9 = WETH9(web3=services.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

        current_balance = services.web3.eth.get_balance(services.web3.eth.default_account)
        console.print(f"Before ETH balance: {to_human(current_balance, decimals=WETH9.decimals())} ETH")
        weth9_balance = weth9.balance_of(services.web3.eth.default_account)
        console.print(f"Before WETH9 balance: {to_human(weth9_balance, decimals=WETH9.decimals())} WETH9")

        amount_in = int(Prompt.ask("Enter amount to wrap (ETH)"))
        wei_amount_in = to_wei(amount_in, decimals=WETH9.decimals())

        transaction_service = TransactionService(web3=services.web3, async_web3=services.async_web3)
        fees = await transaction_service.calculate_tx_fees(gas_limit=120000)

        await transaction_service.send_transaction(
            weth9.deposit(
                amount_in=wei_amount_in,
                gas_limit=fees.gas_limit,
                max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
                max_fee_per_gas=fees.max_fee_per_gas,
            )
        )
        console.print(f"Wrapped {to_human(wei_amount_in, decimals=WETH9.decimals())} ETH into WETH9")

        current_balance = services.web3.eth.get_balance(services.web3.eth.default_account)
        console.print(f"After ETH balance: {to_human(current_balance, decimals=WETH9.decimals())} ETH")
        weth9_balance = weth9.balance_of(services.web3.eth.default_account)
        console.print(f"After WETH9 balance: {to_human(weth9_balance, decimals=WETH9.decimals())} WETH9")

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

    services = create_service(config_dir)

    console.print("")
    console.print("Token balances:\n")
    console.print(f"  ETH: {to_human(services.web3.eth.get_balance(services.web3.eth.default_account), decimals=WETH9.decimals())}")
    weth9 = WETH9(web3=services.web3, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
    console.print(f"WETH9: {to_human(weth9.balance_of(services.web3.eth.default_account), decimals=WETH9.decimals())}")
    dai = DAI(web3=services.web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F")
    console.print(f"  DAI: {to_human(dai.balance_of(services.web3.eth.default_account), decimals=DAI.decimals())}")
    usdc = USDC(web3=services.web3, address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    console.print(f" USDC: {to_human(usdc.balance_of(services.web3.eth.default_account), decimals=USDC.decimals())}")
    wbtc = WBTC(web3=services.web3, address="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")
    console.print(f" WBTC: {to_human(wbtc.balance_of(services.web3.eth.default_account), decimals=WBTC.decimals())}")


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
        services = create_service(config_path=config_dir, passphrase=passphrase)
        order_book_v2 = services.order_book

        order_types = []
        choices = []
        for idx, order_type_idx in enumerate(OrderType):
            console.print(f"{idx}) {order_type_idx.value}")
            order_types.append(order_type_idx)
            choices.append(str(idx))

        order_type_idx = int(Prompt.ask("Choose order type", choices=choices))

        token_routes = order_book_v2.router.get_token_routes()

        tokens = []
        choices = []
        for idx, token in enumerate(token_routes.keys()):
            console.print(f"{idx}) {token}")
            tokens.append(token)
            choices.append(str(idx))

        token0_idx = int(Prompt.ask("Choose token0", choices=choices))
        token0_name = tokens[token0_idx]
        token0 = order_book_v2.token.get_token_by_name(token0_name)

        tokens = []
        choices = []
        for idx, token in enumerate(token_routes[token0.name]):
            console.print(f"{idx}) {token}")
            tokens.append(token)
            choices.append(str(idx))

        token1_idx = int(Prompt.ask("Choose token1", choices=choices))
        token1_name = tokens[token1_idx]
        token1 = order_book_v2.token.get_token_by_name(token1_name)

        exchanges = order_book_v2.router.get_token_pair_by_token0_and_token1(
            token0=token0,
            token1=token1,
        )

        token0_balance = token0.balance_of(order_book_v2.web3.eth.default_account)
        console.print(f"Balance: [green]{to_human(token0_balance, decimals=token0.decimals())} {token0.name}[green]")

        for exchange in exchanges:
            if token0.name == exchange.token0.name:
                console.print(
                    f"Current price on {exchange.name}: {to_human(exchange.calculate_token0_to_token1_amount_out(), decimals=token1.decimals())} {token1.name}"
                )
            else:
                console.print(
                    f"Current price on {exchange.name}: {to_human(exchange.calculate_token1_to_token0_amount_out(), decimals=token1.decimals())} {token1.name}"
                )

        # TODO(mateu.sh): bring back `min_balance_to_transact`
        # if token_in_balance < token_pair.min_balance_to_transact:
        #     console.print(f"You don't have enough tokens")
        #     sys.exit(1)

        trigger_price = Decimal(Prompt.ask("Trigger price"))
        percent_of_tokens = Decimal(Prompt.ask("Percent of tokens to flip (excluding gas fees)", default=str(100)))

        transaction_service = TransactionService(web3=order_book_v2.web3, async_web3=order_book_v2.async_web3)
        fees = await transaction_service.calculate_tx_fees(gas_limit=120000)

        await asyncio.gather(
            transaction_service.send_transaction(
                # UniswapV3 Router
                token0.approve(
                    "0xE592427A0AEce92De3Edee1F18E0157C05861564",
                    max_amount_in=token0_balance,
                    gas_limit=fees.gas_limit,
                    max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
                    max_fee_per_gas=fees.max_fee_per_gas,
                )
            ),
            transaction_service.send_transaction(
                # UniswapV2 Router02
                token0.approve(
                    "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
                    max_amount_in=token0_balance,
                    gas_limit=fees.gas_limit,
                    max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
                    max_fee_per_gas=fees.max_fee_per_gas,
                )
            ),
            transaction_service.send_transaction(
                # PancakeSwap
                token0.approve(
                    "0xEfF92A263d31888d860bD50809A8D171709b7b1c",
                    max_amount_in=token0_balance,
                    gas_limit=fees.gas_limit,
                    max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
                    max_fee_per_gas=fees.max_fee_per_gas,
                )
            ),
            transaction_service.send_transaction(
                # Sushiswap
                token0.approve(
                    "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
                    max_amount_in=token0_balance,
                    gas_limit=fees.gas_limit,
                    max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
                    max_fee_per_gas=fees.max_fee_per_gas,
                )
            ),
        )

        new_order = OrderDto(
            type=order_types[order_type_idx],
            token0=token0,
            token1=token1,
            trigger_price=to_wei(trigger_price, decimals=token1.decimals()),
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
