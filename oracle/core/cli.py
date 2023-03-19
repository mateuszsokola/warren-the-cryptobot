import asyncio
import functools
import os
import sys
import typer
from rich.console import Console
from asyncio import FIRST_COMPLETED, CancelledError

import typer
from web3.middleware import (
    construct_sign_and_send_raw_middleware,
    time_based_cache_middleware,
    simple_cache_middleware,
)
from oracle.core.create_service import create_service
from oracle.utils.format_exception import format_exception
from oracle.utils.logger import logger
from oracle.utils.runner import Runner

main_app = typer.Typer()


@main_app.callback()
def main():
    logger.info(f"Environment variables {os.environ}")

    logger.info(f"Oracle CLI arguments: {str(sys.argv)}")
    # logger.info(f"Started on network={global_options['network']}")


# async def run_catch_up(oracle: Oracle, index_legacy_claims: bool = False, index_nft: bool = False):
#     # need to catch up batch deposits first because we have now
#     # dependency after introducing validator transfers
#     await oracle.process_batch_deposit_logs(initial_run=True)

#     oracle_runner = OracleRunner.getInstance()
#     await asyncio.gather(
#         oracle.process_tx_fee_pool_logs(initial_run=True),
#         oracle_runner.with_conditional_run(
#             functools.partial(oracle.process_nft_related_logs, initial_run=True), predicate=index_nft
#         ),
#         oracle_runner.with_conditional_run(oracle.process_legacy_claims, predicate=index_legacy_claims),
#     )
#     global_options["catch_up_sync_in_progress"] = False


@main_app.command()
def start(
    eth_api_url: str = typer.Option(..., help="Gnosis API"),
    seek_interval: int = typer.Option(5, help="Block seeking interval."),
    gas_limit: int = typer.Option(500000, help="Gas limit"),
):
    async def main():
        console: Console = Console()

        # incorrect_config_dir = SetupWizard.verify_config_path(config_path=config_dir) == False
        # if incorrect_config_dir:
        #     console.print("It seems like the config path does not exist. Did you run the setup script?")
        #     sys.exit(1)

        # passphrase = Prompt.ask("Enter passphrase")

        oracle = create_service(eth_api_url=eth_api_url)
        runner = Runner.getInstance()

        try:
            await oracle.watch_blocks()
            # await oracle.swapcat_sync_balances()
            # await oracle.initial_sync_swapcat()
            # await oracle.initial_sync_levinwap()
            # await oracle.initial_sync_sushiswap()

            # await asyncio.gather(
            #     oracle.initial_sync_swapcat(),
            #     oracle.initial_sync_levinwap(),
            # )
            # logger.info(f"Warren is shutting down now")
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.error(f"[MAIN_THREAD]: {format_exception()}")
            runner.graceful_shutdown()
            sys.exit(1)

    asyncio.run(main())
