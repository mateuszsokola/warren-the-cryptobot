import asyncio
from fractions import Fraction
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
from oracle.core.oracle import Oracle
from oracle.utils.calculate_amount_out import calculate_token0_to_token1_amount_out, calculate_token1_to_token0_amount_out
from oracle.utils.format_exception import format_exception
from oracle.utils.logger import logger
from oracle.utils.runner import Runner

main_app = typer.Typer()

global_options = {}


@main_app.callback()
def main():
    logger.info(f"Environment variables {os.environ}")

    logger.info(f"Oracle CLI arguments: {str(sys.argv)}")
    # logger.info(f"Started on network={global_options['network']}")


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
            await oracle.initial_sync()
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


@main_app.command()
def test_pairs(
    eth_api_url: str = typer.Option(..., help="Gnosis API"),
):
    oracle = create_service(eth_api_url=eth_api_url)
    console: Console = Console()

    res = oracle.store.list_swapcat_offers_with_uniswap_matches()

    # result = calculate_token1_to_token0_amount_out(
    #     reserve0=int(100*10**18), reserve1=int(150000*10**18), amount_in=int(1*10**18)
    # )
    # console.print("RES", result)

    for offer in res:
        console.print(offer)

        pairs = oracle.store.list_uniswap_v2_pairs_by_token(token=offer.token0)
        for pair in pairs:

            if pair.token0 == offer.token0:
                x = calculate_token1_to_token0_amount_out(
                    reserve0=int(pair.reserve0), reserve1=int(pair.reserve1), amount_in=offer.available_balance,
                )
            else:
                x = calculate_token0_to_token1_amount_out(
                    reserve0=int(pair.reserve0), reserve1=int(pair.reserve1), amount_in=offer.available_balance,
                )

            console.print(pair)

     

            p2 = oracle.store.list_uniswap_v2_pairs_by_tokens(token_a=pair.token0, token_b="0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d")
            for pair in p2:
                result = calculate_token0_to_token1_amount_out(
                    reserve0=int(pair.reserve0), reserve1=int(pair.reserve1), amount_in=x,
                )
                console.print(pair)
                console.print("price2", result)

                result = calculate_token1_to_token0_amount_out(
                    reserve0=int(pair.reserve0), reserve1=int(pair.reserve1), amount_in=x,
                )
                # console.print(pair)
                console.print("price2", result)

            print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

    # p2 = oracle.store.list_uniswap_v2_pairs_by_tokens(
    #     token_a="0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1", token_b="0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d"
    # )
    # for pair in p2:
    #     console.print(pair)

    #     result = calculate_token0_to_token1_amount_out(
    #         reserve0=int(pair.reserve0),
    #         reserve1=int(pair.reserve1),
    #         amount_in=int(1 * 10**18),
    #     )
    #     console.print("price2", result)

    #     result = calculate_token1_to_token0_amount_out(
    #         reserve0=int(pair.reserve0),
    #         reserve1=int(pair.reserve1),
    #         amount_in=int(1 * 10**18),
    #     )
    #     # console.print(pair)
    #     console.print("price2", result)

    #     print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")


# pairs = oracle.store.list_uniswap_v2_pairs_by_tokens(token_a="0xb7D311E2Eb55F2f68a9440da38e7989210b9A05e", token_b="0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d")
# for pair in pairs:
#     console.print(pair)
#     result = calculate_token0_to_token1_amount_out(
#         reserve0=int(pair.reserve0), reserve1=int(pair.reserve1), amount_in=int(1*10**18)
#     )
#     console.print("RES", result)
#     console.print("Ra/Rb", int(pair.reserve0) / int(pair.reserve1))
#     console.print("Rb/Ra", int(pair.reserve1) / int(pair.reserve0))
