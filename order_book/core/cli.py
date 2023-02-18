import asyncio
from decimal import Decimal
import os
import sys
import typer
from rich.console import Console
from rich.prompt import Prompt
from warren.core.create_database import create_database
from warren.core.create_service import create_service
from warren.core.setup_wizard import SetupWizard
from order_book.models.order import OrderDto, OrderStatus, OrderType
from warren.services.transaction_service import TransactionService
from order_book.utils.print_order_table import print_order_table
from warren.utils.to_human import to_human
from warren.utils.to_wei import to_wei


order_book_app = typer.Typer()


# TODO(mateu.sh): support ETH wrapping
# TODO(mateu.sh): get rid of repeated code
@order_book_app.command()
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


@order_book_app.command()
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


@order_book_app.command()
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
