import asyncio
from web3.types import TxReceipt
import sys
import typer
from rich.console import Console
from rich.prompt import Prompt
from fluffykitten.core.router import Router
from tokens.base_token import BaseToken
from warren.core.create_service import create_service
from warren.core.setup_wizard import SetupWizard
from warren.managers.transaction_manager import TransactionManager
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

    asyncio.run(main())


@fluffykitten_app.command()
def swap(
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

        transaction_manager = TransactionManager(async_web3=services.async_web3, web3=services.web3)

        dai_token = BaseToken(web3=services.web3, address="0x6B175474E89094C44Da98b954EedeAC495271d0F", name="DAI")
        link_token = BaseToken(web3=services.web3, address="0x514910771AF9Ca656af840dff83E8264EcF986CA", name="LINK")

        dai_amount_in = dai_token.balance_of(services.web3.eth.default_account)
        console.print(f"{to_human(dai_amount_in, decimals=18)} DAI")

        fees = await transaction_manager.calculate_tx_fees(gas_limit=500000)

        await transaction_manager.send_transaction(
            dai_token.approve(
                "0xE592427A0AEce92De3Edee1F18E0157C05861564",
                max_amount_in=dai_amount_in,
                gas_limit=fees.gas_limit,
                max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
                max_fee_per_gas=fees.max_fee_per_gas,
            ),
        )

        await transaction_manager.send_transaction(
            link_token.approve(
                "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
                max_amount_in=dai_amount_in,
                gas_limit=fees.gas_limit,
                max_priority_fee_per_gas=fees.max_priority_fee_per_gas,
                max_fee_per_gas=fees.max_fee_per_gas,
            ),
        )

        paths = router.list_routes()
        max_amount_out = paths[0].calculate_amount_out(dai_amount_in)
        console.print(f"{paths[0].name} - {to_human(max_amount_out, decimals=18)} LINK [blue]EXPECTED[blue]")

        await paths[0].exchange(amount_in=dai_amount_in, min_amount_out=0, gas_limit=500000)

        link_amount_out = link_token.balance_of(services.web3.eth.default_account)
        console.print(f"{paths[0].name} - {to_human(link_amount_out, decimals=18)} LINK")

        dai_amount_out = paths[4].calculate_amount_out(max_amount_out)
        console.print(f"{paths[4].name} - {to_human(dai_amount_out, decimals=18)} DAI [blue]EXPECTED[blue]")

        await paths[4].exchange(amount_in=link_amount_out, min_amount_out=0, gas_limit=500000)

        dai_amount_out = dai_token.balance_of(services.web3.eth.default_account)
        console.print(f"{paths[4].name} - {to_human(dai_amount_out, decimals=18)} DAI")

    asyncio.run(main())
