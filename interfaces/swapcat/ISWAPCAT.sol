// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.12;


interface ISWAPCAT {
    function makeoffer(address _offertoken, address _buyertoken, uint256 _price, uint24 _offerid) external returns (uint24);
    function deleteoffer(uint24 _offerid) external returns (string memory);
    function getoffercount() external view returns (uint24); 
    function tokeninfo(address _tokenaddr) external view returns (uint256, string memory, string memory);
    function showoffer(uint24 _offerid) external view returns (address, address, address, uint256, uint256);
    function pricepreview(uint24 _offerid, uint256 _amount) external view returns (uint256);
    function buy(uint24 _offerid, uint256 _offertokenamount, uint256 _price) external payable returns (string memory);
    function losttokens(address token) external;
}