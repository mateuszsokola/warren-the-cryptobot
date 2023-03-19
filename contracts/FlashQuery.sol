// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.12;
pragma abicoder v2;

import "../interfaces/swapcat/ISWAPCAT.sol";
import "../interfaces/uniswap/v2/IUniswapV2Pair.sol";

contract FlashQuery {
    address private constant swapcatAddress = 0xB18713Ac02Fc2090c0447e539524a5c76f327a3b;

    ISWAPCAT private swapcat = ISWAPCAT(swapcatAddress);

    function batchReservesByPairs(IUniswapV2Pair[] calldata _pairs) external view returns (uint256[3][] memory) {
        uint256[3][] memory result = new uint256[3][](_pairs.length);
        for (uint i = 0; i < _pairs.length; i++) {
            (result[i][0], result[i][1], result[i][2]) = _pairs[i].getReserves();
        }
        return result;
    }

    function batchOfferBalances(uint24[] memory offerIds) external view returns (uint256[] memory) {
        uint24 offerCount = uint24(offerIds.length);
        require(offerCount > 0, "offerIds cannot be empty");
        
        uint256[] memory result = new uint256[](offerCount);

        for (uint24 i = 0; i < offerCount; ++i) {
            uint256 balance;
            (,,,,balance) = swapcat.showoffer(offerIds[i]);
            result[i] = balance;
        }

        return result;
    }
}