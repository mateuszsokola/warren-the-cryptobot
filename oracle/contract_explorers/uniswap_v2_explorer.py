from typing import List
from web3 import Web3
from oracle.core.flash_query import FlashQuery

from oracle.core.store import Store
from oracle.utils.load_contract_abi import load_contract_abi
from oracle.utils.logger import logger


SUSHISWAP_ROUTER = "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"

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

    def __init__(self, web3: Web3, store: Store, flash_query: FlashQuery):
        self.web3 = web3
        self.store = store
        self.flash_query = flash_query
        self.contract = web3.eth.contract(
            Web3.toChecksumAddress(SUSHISWAP_ROUTER),
            abi=load_contract_abi("IUniswapV2Router02.json"),
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
            (_, payload) = self.contract.decode_function_input(input)
            addresses: List[str] = []
            for i in range(0, len(payload["path"]) - 1, 1):
                token_a = payload["path"][i]
                token_b = payload["path"][i + 1]

                for pair in self.store.list_uniswap_v2_pairs_by_tokens(token_a, token_b):
                    addresses.append(pair.address)

            self._update_pairs(addresses=addresses, block_number=block_number)
            return
        elif fn_signature in self.liquidity_eth:
            (_, payload) = self.contract.decode_function_input(input)

            addresses: List[str] = []
            for pair in self.store.list_uniswap_v2_pairs_by_tokens(payload["token"], WETH9):
                addresses.append(pair.address)

            self._update_pairs(addresses=addresses, block_number=block_number)
            return

        elif fn_signature in self.liquidity:
            (_, payload) = self.contract.decode_function_input(input)

            addresses: List[str] = []
            for pair in self.store.list_uniswap_v2_pairs_by_tokens(payload["tokenA"], payload["tokenB"]):
                addresses.append(pair.address)

            self._update_pairs(addresses=addresses, block_number=block_number)
            return
        else:
            logger.warn(f"Unsupported method in block {block_number}")

    def _update_pairs(self, addresses: List[str], block_number: int):
        pairs_to_update = self.flash_query.batch_reserves_by_pairs(addresses)
        self.store.update_pair_reserves(pairs=pairs_to_update)
        logger.info(f"Updated pair count {len(pairs_to_update)} in block {block_number}")
