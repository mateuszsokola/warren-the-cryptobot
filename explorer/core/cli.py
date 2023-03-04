import sys
import typer
from rich.console import Console
from exchanges.mooniswap.factory import MooniSwapFactory
from exchanges.mooniswap.get_tokens_from_address import get_tokens_from_address
from exchanges.uniswap.v2.create_pair_from_address import create_pair_from_address
from exchanges.uniswap.v2.factory import UniswapV2Factory
from explorer.models.pair import PairDto
from warren.core.create_service import create_service
from warren.core.setup_wizard import SetupWizard
from warren.utils.logger import logger


explorer_app = typer.Typer()


@explorer_app.command()
def scan(
    factory_address: str = typer.Option(..., help="Uniswap V2 Factory Address"),
    factory_name: str = typer.Option(..., help="Uniswap V2 Name"),
    config_dir: str = typer.Option(SetupWizard.default_config_path(), help="Path to the config directory."),
):
    console: Console = Console()

    incorrect_config_dir = SetupWizard.verify_config_path(config_path=config_dir) == False
    if incorrect_config_dir:
        console.print("It seems like the config path does not exist. Did you run the setup script?")
        sys.exit(1)

    services = create_service(config_dir)

    factory = UniswapV2Factory(web3=services.web3, address=factory_address)
    length = factory.get_pairs_length()

    for index in range(0, length, 1):
        address = factory.get_pair_address_by_index(index)
        contract = create_pair_from_address(web3=services.web3, address=address)

        (reserve0, reserve1, timestamp) = contract.functions.getReserves().call()
        token0 = contract.functions.token0().call()
        token1 = contract.functions.token1().call()

        pair = PairDto(
            type=factory_name,
            address=address,
            timestamp=timestamp,
            reserve0=reserve0,
            reserve1=reserve1,
            token0=token0,
            token1=token1,
        )
        services.database.insert_or_replace_pair(pair)
        logger.info(f"{index}/{length}")


@explorer_app.command()
def scan_mooniswap(
    config_dir: str = typer.Option(SetupWizard.default_config_path(), help="Path to the config directory."),
):
    console: Console = Console()

    incorrect_config_dir = SetupWizard.verify_config_path(config_path=config_dir) == False
    if incorrect_config_dir:
        console.print("It seems like the config path does not exist. Did you run the setup script?")
        sys.exit(1)

    services = create_service(config_dir)

    factory = MooniSwapFactory(web3=services.web3, address="0x71CD6666064C3A1354a3B4dca5fA1E2D3ee7D303")
    pools = factory.get_all_pools()

    for idx, address in enumerate(pools):
        (token0, token1) = get_tokens_from_address(web3=services.web3, address=address)
        pair = PairDto(
            type="mooniswap",
            address=address,
            token0=token0,
            token1=token1,
        )
        services.database.insert_or_replace_pair(pair)
        logger.info(f"{idx}/{len(pools)}")
