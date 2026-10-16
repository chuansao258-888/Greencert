// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface ICertificateRegistry {
    // Update a certificate's listing state.
    function setListed(uint256 certificateId, address seller, bool listed) external;
    // Transfer the entire certificate after a market sale.
    function transferOnSale(uint256 certificateId, address seller, address buyer) external;
    // Read a certificate's immutable batch quantity.
    function certificateQuantity(uint256 certificateId) external view returns (uint32);
}
