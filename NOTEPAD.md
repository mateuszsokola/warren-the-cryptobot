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


@main_app.command()
def test_pairs(
    eth_api_url: str = typer.Option(..., help="Gnosis API"),
):
    passphrase = Prompt.ask("Enter passphrase")
    oracle = create_service(eth_api_url=eth_api_url, passphrase=passphrase)
    console: Console = Console()

    # contract = oracle.web3.eth.contract(
    #     address="0x1CF2fc76128A0b3ee2f1093bA11F534998e72FF1",
    #     abi=load_contract_abi("IUniswapV2Pair.json"),
    # )

    # token0 = contract.functions.token0().call()
    # token1 = contract.functions.token1().call()
    # (reserve0, reserve1, timestamp) = contract.functions.getReserves().call()

    # console.print(token0, token1, reserve0, reserve1, timestamp)

    # console.print(res)

    # result = calculate_token1_to_token0_amount_out(
    #     reserve0=int(100*10**18), reserve1=int(150000*10**18), amount_in=int(1*10**18)
    # )
    # console.print("RES", result)

    # SwapcatOffer(
    #     id=6892,
    #     block_number=27100731,
    #     token0='0x2089b1b815A2FD0187a48a1C66C511DA828a8128',
    #     token1='0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83',
    #     recipient='0xCbcDCA647cFda9283992193604F8718A910b42fc',
    #     amount=67000000,
    #     available_balance=975000000000000000
    # )



    result = calculate_token0_to_token1_amount_out(
        reserve0=int(369977184262970768278),
        reserve1=int(15377771185608607),
        amount_in=int(10000000000000000000),
    )

    console.print("HoneySwap 0-1", result)

    result = calculate_token1_to_token0_amount_out(
        reserve0=int(369977184262970768278),
        reserve1=int(15377771185608607),
        amount_in=int(10000000000000000000),
    )

    console.print("HoneySwap 1-0", result)


    result = calculate_token0_to_token1_amount_out(
        reserve0=int(5789520987006555896535),
        reserve1=int(221114392807086496),
        amount_in=int(10000000000000000000),
    )

    console.print("SushiSwap 0-1", result)


    result = calculate_token1_to_token0_amount_out(
        reserve0=int(5789520987006555896535),
        reserve1=int(221114392807086496),
        amount_in=int(10000000000000000000),
    )

    console.print("SushiSwap 1-0", result)

    # res = oracle.store.list_uniswap_v2_pairs()
    # path_finder = PathFinder(store=oracle.store)

    # for pair in res:
    #     result = path_finder.find([offer.token1, offer.token0], [offer.available_balance])
    #     token = oracle.store.find_token_by_address(offer.token0)

    #     unit_amount = Decimal(offer.available_balance) / Decimal(10**token.decimals)
    #     final_price = int(unit_amount * offer.amount)

    #     if result is not None and result[0][1][len(result[0][1]) - 1] > final_price:
    #         console.print(offer)
    #         console.print(result)

    # result = calculate_token0_to_token1_amount_out(
    #     reserve0=int(29954728179209306592),
    #     reserve1=int(1613844931),
    #     amount_in=int(1975000000000000000),
    # )
    # # console.print(pair)
    # console.print("price2", result)

    # result = calculate_token1_to_token0_amount_out(
    #     reserve0=int(29954728179209306592),
    #     reserve1=int(1613844931),
    #     amount_in=int(1975000000000000000),
    # )
    # # console.print(pair)
    # console.print("price2", result)

    # for offer in res:
    #     console.print(offer)

    # pairs = oracle.store.list_uniswap_v2_pairs_by_token(token=offer.token0)
    # for pair in pairs:

    #     if pair.token0 == offer.token0:
    #         x = calculate_token1_to_token0_amount_out(
    #             reserve0=int(pair.reserve0),
    #             reserve1=int(pair.reserve1),
    #             amount_in=offer.available_balance,
    #         )
    #     else:
    #         x = calculate_token0_to_token1_amount_out(
    #             reserve0=int(pair.reserve0),
    #             reserve1=int(pair.reserve1),
    #             amount_in=offer.available_balance,
    #         )

    # p2 = oracle.store.list_uniswap_v2_pairs_by_tokens(
    #     token_a=pair.token0, token_b="0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d"
    # )
    # for pair in p2:
    #     result = calculate_token0_to_token1_amount_out(
    #         reserve0=int(pair.reserve0),
    #         reserve1=int(pair.reserve1),
    #         amount_in=x,
    #     )
    #     console.print(pair)
    #     console.print("price2", result)

    #     result = calculate_token1_to_token0_amount_out(
    #         reserve0=int(pair.reserve0),
    #         reserve1=int(pair.reserve1),
    #         amount_in=x,
    #     )
    #     # console.print(pair)
    #     console.print("price2", result)

    # print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

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

"""
select
    u.id,
    u.type,
    u.address,
    t0.symbol,
    t1.symbol,
    u.reserve0,
    u.reserve1,
    u.timestamp
from uniswap_v2_pairs u
left join tokens t0 on (t0.address = u.token0)
left join tokens t1 on (t1.address = u.token1)
where reserve0 > 0 and reserve1 > 0 and type="levinswap";
"""

"""
select
    u.id,
    u.type,
    u.address,
    t0.symbol,
    t1.symbol,
    u.reserve0,
    u.reserve1,
    u.timestamp
from uniswap_v2_pairs u
left join tokens t0 on (t0.address = u.token0)
left join tokens t1 on (t1.address = u.token1)
where 
reserve0 > 0 and reserve1 > 0 and 
token0 not in ("0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83", "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d", "0x8e5bBbb09Ed1ebdE8674Cda39A0c169401db4252", "0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1") and
token1 not in ("0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83", "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d", "0x8e5bBbb09Ed1ebdE8674Cda39A0c169401db4252", "0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1");
"""


"""
0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83, # USDC
0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d, # WXDAI
0x8e5bBbb09Ed1ebdE8674Cda39A0c169401db4252, # WBTC
0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1  # WETH9

"""


"""
select
    u.id,
    u.type,
    u.address,
    t0.symbol,
    t1.symbol,
    u.reserve0,
    u.reserve1,
    u.timestamp
from uniswap_v2_pairs u
left join tokens t0 on (t0.address = u.token0)
left join tokens t1 on (t1.address = u.token1)
where 
reserve0 > 0 and reserve1 > 0 and 
token0 not in ("0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83", "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d", "0x8e5bBbb09Ed1ebdE8674Cda39A0c169401db4252", "0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1") and
token1 not in ("0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83", "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d", "0x8e5bBbb09Ed1ebdE8674Cda39A0c169401db4252", "0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1") and
(token0 = "0x4A88248BAa5b39bB4A9CAa697Fb7f8ae0C3f0ddB" or token1 = "0x4A88248BAa5b39bB4A9CAa697Fb7f8ae0C3f0ddB");
"""


"""
select
token0, token1, count(*) as c
from uniswap_v2_pairs u
left join tokens t0 on (t0.address = u.token0)
left join tokens t1 on (t1.address = u.token1)
where reserve0 > 0 and reserve1 > 0 
group by token0, token1
order by c asc 
"""


"""
select
    u.id,
    u.type,
    u.address,
    t0.symbol,
    t1.symbol,
    u.reserve0,
    u.reserve1,
    u.timestamp
from uniswap_v2_pairs u
left join tokens t0 on (t0.address = u.token0)
left join tokens t1 on (t1.address = u.token1)
WHERE token0 = "0xe0d0b1DBbCF3dd5CAc67edaf9243863Fd70745DA" and token1 = "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d"
"""
