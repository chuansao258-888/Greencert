// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../../contracts/RoleRegistry.sol";
import "../../contracts/CertificateRegistry.sol";
import "../../contracts/CertificateMarket.sol";

contract TestActor {
    // Accept sale proceeds in the contract tests.
    receive() external payable {}

    // Register this actor with the requested role.
    function register(RoleRegistry roles, uint8 role) external {
        roles.register(role);
    }

    // Submit a small generation batch from this actor.
    function submit(CertificateRegistry registry, uint32 index, uint32 quantity) external returns (uint256) {
        return registry.submitApplication(bytes32(uint256(1)), uint64(block.timestamp - 100), uint64(block.timestamp - 1), index, quantity, bytes32(uint256(2)));
    }

    // Withdraw this actor's pending application.
    function withdrawApplication(CertificateRegistry registry, uint256 id) external {
        registry.withdrawApplication(id);
    }

    // List an owned certificate for sale.
    function list(CertificateMarket market, uint256 id, uint256 price) external {
        market.listCertificate(id, price);
    }

    // Change the price of this actor's listing.
    function updatePrice(CertificateMarket market, uint256 id, uint256 price) external {
        market.updatePrice(id, price);
    }

    // Cancel this actor's active listing.
    function cancel(CertificateMarket market, uint256 id) external {
        market.cancelListing(id);
    }

    // Buy a certificate using the supplied payment.
    function buy(CertificateMarket market, uint256 id, uint256 price) external payable {
        market.buyCertificate{value: msg.value}(id, price);
    }

    // Withdraw this actor's sale proceeds.
    function withdrawProceeds(CertificateMarket market) external {
        market.withdraw();
    }

    // Retire this actor's purchased certificate.
    function retire(CertificateRegistry registry, uint256 id) external {
        registry.retireCertificate(id, bytes32(uint256(3)));
    }
}
