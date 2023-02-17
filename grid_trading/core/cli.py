import asyncio
from decimal import Decimal
import os
import sys
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from grid_trading.models.order import GridTradingOrderDto, GridTradingOrderStatus
from warren.core.create_service import create_service
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

        exchange_list = services.grid_trading.router.get_token_pair_by_token0_and_token1(
            token0=token0,
            token1=token1,
        )
        exchange_manager = ExchangeManager(exchange_list=exchange_list, token0=token0, token1=token1)
        table = create_token_prices_by_exchange_table(exchange_manager)
        console.print(table)

        grid_every_percent = Decimal(Prompt.ask("Grid every `n` percent"))
        # console.print(
        #     f"SIMULATION FOR THE FIRST TX ONLY! Tokens will be bought when price on any exchange drops below {to_human(int(exchange_manager.lowest_price[2]), decimals=token1.decimals())} {token1.name}"
        # )

        percent_of_tokens = Decimal(Prompt.ask("Percent of tokens per flip (excluding gas fees)"))

        confirm = Confirm.ask("is it correct?")

        if confirm is False:
            console.print(f"Operation cancelled.")
            sys.exit(0)

        transaction_service = TransactionService(web3=services.web3, async_web3=services.async_web3)
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

        new_order = GridTradingOrderDto(
            token0=token0,
            token1=token1,
            reference_price=exchange_manager.highest_price[2],
            last_tx_price=None,
            grid_every_percent=Decimal(grid_every_percent / Decimal(100)),
            percent_per_flip=Decimal(percent_of_tokens / Decimal(100)),
            status=GridTradingOrderStatus.active,
        )
        services.database.create_grid_trading_order(order=new_order)

        console.print(f"The new order has been created.")

        #
        # TODO
        # ======
        # - [X] - Persist strategy in database (maybe warren_options? - wrong i'd say) include current prices
        # - [X] - Implement trading bot
        # - [X] - Record trxs in database
        # - [ ] - Move order book to separate CLI group
        # - [ ] - Allow tokens to execute trxs (all relevant routers)
        # - [ ] - Display warning if amount of tokens doens't allow to execute any trx

    asyncio.run(main())
