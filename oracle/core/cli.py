import asyncio
from decimal import Decimal
from fractions import Fraction
import functools
import itertools
import json
import os
import sys
import typer
from eth_account.messages import SignableMessage
from rich.console import Console
from rich.prompt import Prompt
from asyncio import FIRST_COMPLETED, CancelledError
import networkx as nx

import typer
from web3 import Web3
from web3.middleware import (
    construct_sign_and_send_raw_middleware,
    time_based_cache_middleware,
    simple_cache_middleware,
)
from oracle.core.create_service import create_service
from oracle.core.oracle import Oracle
from oracle.core.path_finder import PathFinder
from oracle.core.transaction_manager import TransactionManager
from oracle.exchanges.uniswap.v2.models.exact_tokens_for_tokens_params import ExactTokensForTokensParams
from oracle.exchanges.uniswap.v2.router import UniswapV2Router
from oracle.utils.calculate_amount_out import calculate_token0_to_token1_amount_out, calculate_token1_to_token0_amount_out
from oracle.utils.format_exception import format_exception
from oracle.utils.load_contract_abi import load_contract_abi
from oracle.utils.logger import logger
from oracle.utils.runner import Runner
from oracle.watchers.block_watcher import SUSHISWAP_ROUTER

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

        passphrase = Prompt.ask("Enter passphrase")
        oracle = create_service(eth_api_url=eth_api_url, passphrase=passphrase)
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
def execute(
    eth_api_url: str = typer.Option(..., help="Gnosis API"),
):
    async def main():
        passphrase = Prompt.ask("Enter passphrase")
        oracle = create_service(eth_api_url=eth_api_url, passphrase=passphrase)
        console: Console = Console()

        console.print(f"Balance: {oracle.web3.eth.get_balance(oracle.web3.eth.default_account)} xDai")

        usdc = oracle.web3.eth.contract(
            address="0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83",
            abi=load_contract_abi("IPermittableToken.json"),
        )

        wxdai = oracle.web3.eth.contract(
            address="0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d",
            abi=load_contract_abi("WXDAI.json", "artifacts/tokens"),
        )
        console.print(f"Balance: {usdc.functions.balanceOf(oracle.web3.eth.default_account).call()} USDC")
        console.print(f"Balance: {wxdai.functions.balanceOf(oracle.web3.eth.default_account).call()} wxDai")

        transaction_manager = TransactionManager(web3=oracle.web3, async_web3=oracle.async_web3)

        # # Swap xDAI to USDC

        # tx_fees = await transaction_manager.calculate_tx_fees(500000)

        # sushiswap_router = UniswapV2Router(web3=oracle.web3, address=SUSHISWAP_ROUTER)
        # params = ExactTokensForTokensParams(
        #     path=["0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d", "0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83"],
        #     amount_in=int(100 * 10**18),
        #     amount_out_minimum=int(99 * 10**6),
        #     deadline=9999999999,
        #     recipient=oracle.web3.eth.default_account,
        # )

        # tx_params = sushiswap_router.swap_exact_ETH_for_tokens(
        #     params, tx_fees.gas_limit, tx_fees.max_priority_fee_per_gas, tx_fees.max_fee_per_gas
        # )
        # await transaction_manager.send_transaction(tx_params)

        # console.print(f"Balance: {usdc.functions.balanceOf(oracle.web3.eth.default_account).call()} USDC")

        # encode_structured_data

        # domain = {
        #     "name": "USD//C on xDai",
        #     "version": "1",
        #     "chainId": 100,
        #     "verifyingContract": "0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83",
        # }

        # message = {
        #     "holder": oracle.web3.eth.default_account,
        #     "spender": "0xC759AA7f9dd9720A1502c104DaE4F9852bb17C14",
        #     "nonce": nonce,
        #     "expiry": "1680187955",
        #     "allowed": True,
        # }

        # header = {
        #     "types": {
        #         "Permit": [
        #             {
        #                 "name": "holder",
        #                 "type": "address",
        #             },
        #             {
        #                 "name": "spender",
        #                 "type": "address",
        #             },
        #             {
        #                 "name": "nonce",
        #                 "type": "uint256",
        #             },
        #             {
        #                 "name": "expiry",
        #                 "type": "uint256",
        #             },
        #             {
        #                 "name": "allowed",
        #                 "type": "bool",
        #             },
        #         ]
        #     },
        #     "domain": {
        #         "name": "USD//C on xDai",
        #         "version": "1",
        #         "chainId": 100,
        #         "verifyingContract": "0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83",
        #     },
        # }

        # message = SignableMessage(
        #     version=int(1).to_bytes(1, "little"),
        #     header=bytes(json.dumps(header), "utf-8"),
        #     body=bytes(json.dumps(message), "utf-8"),
        # )
        # signature = oracle.account.sign_message(message)
        # console.print(f"Data: {signature}")

        # swapcat_v2 = oracle.web3.eth.contract(
        #     "0xC759AA7f9dd9720A1502c104DaE4F9852bb17C14",
        #     abi=load_contract_abi("IRealTokenYamUpgradeableV3.json"),
        # )

        swapcat = oracle.web3.eth.contract(
            "0xB18713Ac02Fc2090c0447e539524a5c76f327a3b",
            abi=load_contract_abi("ISWAPCAT.json"),
        )

        tx_fees = await transaction_manager.calculate_tx_fees(500000)

        # tx_params = wxdai.functions.deposit().build_transaction(
        #     {
        #         "type": 2,
        #         "gas": tx_fees.gas_limit,
        #         "maxPriorityFeePerGas": tx_fees.max_priority_fee_per_gas,
        #         "maxFeePerGas": tx_fees.max_fee_per_gas,
        #         "value": 64675001000000000000
        #     }
        # )
        # await transaction_manager.send_transaction(tx_params)

        tx_params = usdc.functions.approve("0xB18713Ac02Fc2090c0447e539524a5c76f327a3b", 64707100).build_transaction(
            {
                "type": 2,
                "gas": tx_fees.gas_limit,
                "maxPriorityFeePerGas": tx_fees.max_priority_fee_per_gas,
                "maxFeePerGas": tx_fees.max_fee_per_gas,
            }
        )
        await transaction_manager.send_transaction(tx_params)

        console.print(f"Balance: {usdc.functions.balanceOf(oracle.web3.eth.default_account).call()} USDC")
        console.print(f"Balance: {wxdai.functions.balanceOf(oracle.web3.eth.default_account).call()} wxDai")

        tx_params = swapcat.functions.buy(9976, 1000000000000000000, 1).build_transaction(
            {
                "type": 2,
                "gas": tx_fees.gas_limit,
                "maxPriorityFeePerGas": tx_fees.max_priority_fee_per_gas,
                "maxFeePerGas": tx_fees.max_fee_per_gas,
            }
        )
        await transaction_manager.send_transaction(tx_params)

        # tx_params = swapcat_v2.functions.buyOfferBatch([7330], [58360000], [1000000000000000000]).build_transaction(
        #     {
        #         "type": 2,
        #         "gas": tx_fees.gas_limit,
        #         "maxPriorityFeePerGas": tx_fees.max_priority_fee_per_gas,
        #         "maxFeePerGas": tx_fees.max_fee_per_gas,
        #     }
        # )
        # await transaction_manager.send_transaction(tx_params)

    asyncio.run(main())


WXDAI = "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d"


def getAmountIn(
    token0,
    token1,
    reserves_token0,
    reserves_token1,
    fee,
    token_out_quantity,
    token_in,
):
    if token_in == token0:
        return int((reserves_token0 * token_out_quantity) // ((1 - fee) * (reserves_token1 - token_out_quantity)) + 1)

    if token_in == token1:
        return int((reserves_token1 * token_out_quantity) // ((1 - fee) * (reserves_token0 - token_out_quantity)) + 1)


def getAmountOut(
    token0,
    token1,
    reserves_token0,
    reserves_token1,
    fee,
    token_in_quantity,
    token_in,
):
    if token_in == token0:
        return int(reserves_token1 * token_in_quantity * (1 - fee)) // int(reserves_token0 + token_in_quantity * (1 - fee))

    if token_in == token1:
        return int(reserves_token0 * token_in_quantity * (1 - fee)) // int(reserves_token1 + token_in_quantity * (1 - fee))


def calc_profit(token0, token1, reserves_token0, reserves_token1, borrow_amount):
    # get repayment INPUT at borrow_amount OUTPUT
    flash_repay_amount = getAmountIn(
        reserves_token0=x0a,
        reserves_token1=y0a,
        fee=Fraction(3, 1000),
        token_out_quantity=borrow_amount,
        token_in="token0",
    )

    swap_amount_out = getAmountOut(
        reserves_token0=x0b,
        reserves_token1=y0b,
        fee=Fraction(3, 1000),
        token_in_quantity=borrow_amount,
        token_in="token1",
    )

    return swap_amount_out - flash_repay_amount


@main_app.command()
def test_pairs(
    eth_api_url: str = typer.Option(..., help="Gnosis API"),
):
    passphrase = Prompt.ask("Enter passphrase")
    oracle = create_service(eth_api_url=eth_api_url, passphrase=passphrase)
    console: Console = Console()

    pairs = oracle.store.list_uniswap_v2_pairs()

    G = nx.MultiGraph()
    for pair in pairs:
        G.add_edge(
            pair.token0,
            pair.token1,
            lp_address=pair.address,
            pool_type="UniswapV2",
        )

    console.print(f"G ready: {len(G.nodes)} nodes, {len(G.edges)} edges")

    all_tokens_with_wxdai_pool = list(G.neighbors(WXDAI))
    console.print(f"Found {len(all_tokens_with_wxdai_pool)} tokens with a WXDAI pair")

    console.print("*** Finding triangular arbitrage paths ***")
    triangle_arb_paths = {}

    filtered_tokens = [token for token in all_tokens_with_wxdai_pool if G.degree(token) > 1]
    console.print(f"Processing {len(filtered_tokens)} tokens with degree > 1")

    for token_a, token_b in itertools.combinations(filtered_tokens, 2):
        # find tokenA/tokenB pools, skip if a tokenA/tokenB pool is not found
        if not G.get_edge_data(token_a, token_b):
            continue

        inside_pools = [edge.get("lp_address") for edge in G.get_edge_data(token_a, token_b).values()]

        # find tokenA/WETH pools
        outside_pools_tokenA = [edge.get("lp_address") for edge in G.get_edge_data(token_a, WXDAI).values()]

        # find tokenB/WETH pools
        outside_pools_tokenB = [edge.get("lp_address") for edge in G.get_edge_data(token_b, WXDAI).values()]

        # find all triangular arbitrage paths of form:
        # tokenA/WETH -> tokenA/tokenB -> tokenB/WETH
        for pool_addresses in itertools.product(outside_pools_tokenA, inside_pools, outside_pools_tokenB):
            pool_data = {}
            pool_info = {}
            for pool_address in pool_addresses:
                pair = oracle.store.find_uniswap_v2_pool_by_address(pool_address)
                pool_info[pool_address] = pair

            pool_data.update(pool_info)
            pool_info = {}

            triangle_arb_paths[id] = {
                "id": (id := Web3.keccak(hexstr="".join([pool_address[2:] for pool_address in pool_addresses])).hex()),
                "path": pool_addresses,
                "pools": pool_data,
            }

    # console.print(triangle_arb_paths)
    print(f"Found {len(triangle_arb_paths)} triangle arb paths")

    path = triangle_arb_paths["0x750850309b60d90aad17e6beb1adab5fef5367f13aa8ee893b21ed9ab3cb7b60"]
    console.print(path)
