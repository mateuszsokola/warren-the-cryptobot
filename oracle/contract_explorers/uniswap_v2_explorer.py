import asyncio
from typing import List
from web3 import Web3
from oracle.contract_explorers.token_explorer import TokenExplorer
from oracle.core.flash_query import FlashQuery

from oracle.core.store import Store
from oracle.models.uniswap.pair import UniswapV2PairDto
from oracle.utils.load_contract_abi import load_contract_abi
from oracle.utils.logger import logger


WETH9 = "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d"


class UniswapV2Explorer:
    # Router 01
    addLiquidity_fn_signature = Web3.toHex(
        Web3.keccak(text="addLiquidity(address,address,uint256,uint256,uint256,uint256,address,uint256)")
    )[2:10]
    addLiquidityETH_fn_signature = Web3.toHex(Web3.keccak(text="addLiquidityETH(address,uint256,uint256,uint256,address,uint256)"))[
        2:10
    ]
    removeLiquidity_fn_signature = Web3.toHex(
        Web3.keccak(text="removeLiquidity(address,address,uint256,uint256,uint256,address,uint256)")
    )[2:10]
    removeLiquidityETH_fn_signature = Web3.toHex(
        Web3.keccak(text="removeLiquidityETH(address,uint256,uint256,uint256,address,uint256)")
    )[2:10]
    removeLiquidityWithPermit_fn_signature = Web3.toHex(
        Web3.keccak(
            text="removeLiquidityWithPermit(address,address,uint256,uint256,uint256,address,uint256,bool,uint8,bytes32,bytes32)"
        )
    )[2:10]
    removeLiquidityETHWithPermit_fn_signature = Web3.toHex(
        Web3.keccak(text="removeLiquidityETHWithPermit(address,uint256,uint256,uint256,address,uint256,bool,uint8,bytes32,bytes32)")
    )[2:10]
    swapExactTokensForTokens_fn_signature = Web3.toHex(
        Web3.keccak(text="swapExactTokensForTokens(uint256,uint256,address[],address,uint256)")
    )[2:10]
    swapExactETHForTokens_fn_signature = Web3.toHex(Web3.keccak(text="swapExactETHForTokens(uint256,address[],address,uint256)"))[
        2:10
    ]
    swapTokensForExactETH_fn_signature = Web3.toHex(
        Web3.keccak(text="swapTokensForExactETH(uint256,uint256,address[],address,uint256)")
    )[2:10]
    swapExactTokensForETH_fn_signature = Web3.toHex(
        Web3.keccak(text="swapExactTokensForETH(uint256,uint256,address[],address,uint256)")
    )[2:10]
    swapETHForExactTokens_fn_signature = Web3.toHex(Web3.keccak(text="swapETHForExactTokens(uint256,address[],address,uint256)"))[
        2:10
    ]
    swapTokensForExactTokens_fn_signature = Web3.toHex(
        Web3.keccak(text="swapTokensForExactTokens(uint256,uint256,address[],address,uint256)")
    )[2:10]

    # Router 02
    removeLiquidityETHSupportingFeeOnTransferTokens_fn_signature = Web3.toHex(
        Web3.keccak(text="removeLiquidityETHSupportingFeeOnTransferTokens(address,uint256,uint256,uint256,address,uint256)")
    )[2:10]
    removeLiquidityETHWithPermitSupportingFeeOnTransferTokens_fn_signature = Web3.toHex(
        Web3.keccak(
            text="removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(address,uint256,uint256,uint256,address,uint256,bool,uint8,bytes32,bytes32)"
        )
    )[2:10]
    swapExactTokensForTokensSupportingFeeOnTransferTokens_fn_signature = Web3.toHex(
        Web3.keccak(text="swapExactTokensForTokensSupportingFeeOnTransferTokens(uint256,uint256,address[],address,uint256)")
    )[2:10]
    swapExactETHForTokensSupportingFeeOnTransferTokens_fn_signature = Web3.toHex(
        Web3.keccak(text="swapExactETHForTokensSupportingFeeOnTransferTokens(uint256,address[],address,uint256)")
    )[2:10]
    swapExactTokensForETHSupportingFeeOnTransferTokens_fn_signature = Web3.toHex(
        Web3.keccak(text="swapExactTokensForETHSupportingFeeOnTransferTokens(uint256,uint256,address[],address,uint256)")
    )[2:10]

    def __init__(
        self,
        web3: Web3,
        store: Store,
        flash_query: FlashQuery,
        token_explorer: TokenExplorer,
        name: str,
        router_address: str,
        factory_address: str,
    ):
        self.web3 = web3
        self.store = store
        self.name = name
        self.flash_query = flash_query
        self.token_explorer = token_explorer
        self.router = web3.eth.contract(
            Web3.toChecksumAddress(router_address),
            abi=load_contract_abi("IUniswapV2Router02.json"),
        )
        self.factory = web3.eth.contract(
            Web3.toChecksumAddress(factory_address),
            abi=load_contract_abi("IUniswapV2Factory.json"),
        )

        self.liquidity = [
            self.addLiquidity_fn_signature,
            self.removeLiquidity_fn_signature,
            self.removeLiquidityWithPermit_fn_signature,
        ]
        self.liquidity_eth = [
            self.addLiquidityETH_fn_signature,
            self.removeLiquidityETH_fn_signature,
            self.removeLiquidityETHWithPermit_fn_signature,
            self.removeLiquidityETHSupportingFeeOnTransferTokens_fn_signature,
            self.removeLiquidityETHWithPermitSupportingFeeOnTransferTokens_fn_signature,
        ]
        self.swaps = [
            self.swapExactTokensForTokens_fn_signature,
            self.swapTokensForExactTokens_fn_signature,
            self.swapExactETHForTokens_fn_signature,
            self.swapTokensForExactETH_fn_signature,
            self.swapExactTokensForETH_fn_signature,
            self.swapETHForExactTokens_fn_signature,
            self.swapExactTokensForTokensSupportingFeeOnTransferTokens_fn_signature,
            self.swapExactETHForTokensSupportingFeeOnTransferTokens_fn_signature,
            self.swapExactTokensForETHSupportingFeeOnTransferTokens_fn_signature,
        ]

    def process_tx(self, input: str, block_number: int) -> List:
        fn_signature = input[2:10]

        if fn_signature in self.swaps:
            (_, payload) = self.router.decode_function_input(input)
            addresses: List[str] = []
            for i in range(0, len(payload["path"]) - 1, 1):
                token_a = payload["path"][i]
                token_b = payload["path"][i + 1]

                for pair in self.store.list_uniswap_v2_pairs_by_tokens(token_a, token_b):
                    addresses.append(pair.address)

            self._update_pairs(addresses=addresses, block_number=block_number)
            return
        elif fn_signature in self.liquidity_eth:
            (_, payload) = self.router.decode_function_input(input)

            addresses: List[str] = []
            for pair in self.store.list_uniswap_v2_pairs_by_tokens(payload["token"], WETH9):
                addresses.append(pair.address)

            self._update_pairs(addresses=addresses, block_number=block_number)
            return

        elif fn_signature in self.liquidity:
            (_, payload) = self.router.decode_function_input(input)

            addresses: List[str] = []
            for pair in self.store.list_uniswap_v2_pairs_by_tokens(payload["tokenA"], payload["tokenB"]):
                addresses.append(pair.address)

            self._update_pairs(addresses=addresses, block_number=block_number)
            return
        else:
            logger.warn(f"Unsupported method in block {block_number}")

    async def sync_pairs(self, block_number: int):
        pair_count = self.factory.functions.allPairsLength().call()

        for idx in range(0, pair_count, 1):
            address = self.factory.functions.allPairs(idx).call()

            (token0, token1, reserve0, reserve1, timestamp) = self._create_pair_from_address(pair_address=address)
            pair = UniswapV2PairDto(
                type=self.name,
                address=address,
                token0=token0,
                token1=token1,
                reserve0=reserve0,
                reserve1=reserve1,
                timestamp=timestamp,
            )
            self.store.insert_or_replace_pair(pair)
            self.token_explorer.discover_token(token0)
            self.token_explorer.discover_token(token1)
            # self.store.set_last_sync_state(self.name.lower(), block_number=block_number, last_idx=idx)
            self.store.con.commit()

            logger.info(f"DEX {self.name} - Pair {idx} / {pair_count}")
            await asyncio.sleep(0)

    def _create_pair_from_address(self, pair_address: str):
        contract = self.web3.eth.contract(
            address=pair_address,
            abi=load_contract_abi("IUniswapV2Pair.json"),
        )

        token0 = contract.functions.token0().call()
        token1 = contract.functions.token1().call()
        (reserve0, reserve1, timestamp) = contract.functions.getReserves().call()

        return (token0, token1, reserve0, reserve1, timestamp)

    def _update_pairs(self, addresses: List[str], block_number: int):
        pairs_to_update = self.flash_query.batch_reserves_by_pairs(addresses)
        self.store.update_pair_reserves(pairs=pairs_to_update)
        logger.info(f"Updated pair count {len(pairs_to_update)} in block {block_number}")
