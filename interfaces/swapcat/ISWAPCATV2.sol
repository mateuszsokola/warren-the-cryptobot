// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.12;


interface ISWAPCATV2 {
    function getOfferCount() external view returns (uint256); 
    function getInitialOffer(uint256 offerId) external view returns (address, address, address, address, uint256, uint256); 
    function showOffer(uint256 offerId) external view returns (address, address, address, address, uint256, uint256); 
}