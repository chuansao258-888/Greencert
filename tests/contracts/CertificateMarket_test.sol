// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./TestActors.sol";
import "remix_tests.sol";

contract CertificateMarketTest {
    // Reject certificate and role registries that refer to different deployments.
    function test_rejects_mismatched_registries() public {
        RoleRegistry roles = new RoleRegistry(address(this));
        RoleRegistry otherRoles = new RoleRegistry(address(this));
        CertificateRegistry registry = new CertificateRegistry(address(roles));
        bool rejected;
        try new CertificateMarket(address(otherRoles), address(registry)) {} catch {
            rejected = true;
        }
        Assert.ok(rejected, "Mismatched registries were accepted");
    }

    // Both registered roles may sell and buy; ownership governs the operation.
    function fixture() private returns (CertificateRegistry registry, CertificateMarket market, TestActor producer, TestActor buyer) {
        RoleRegistry roles = new RoleRegistry(address(this));
        producer = new TestActor();
        buyer = new TestActor();
        producer.register(roles, 2);
        buyer.register(roles, 1);
        registry = new CertificateRegistry(address(roles));
        market = new CertificateMarket(address(roles), address(registry));
        registry.setMarket(address(market));
        producer.submit(registry, 1, 25);
        registry.approveApplication(1);
    }

    // List, reprice and cancel the complete certificate batch.
    function test_owner_lists_updates_and_cancels() public {
        (CertificateRegistry registry, CertificateMarket market, TestActor producer, ) = fixture();
        producer.list(market, 1, 100);
        producer.updatePrice(market, 1, 120);
        require(market.getListing(1).totalPriceWei == 120, "Price not updated");
        producer.cancel(market, 1);
        Assert.ok(!registry.getCertificate(1).listed, "Listing not cancelled");
    }

    // Purchase the complete batch for its exact total price.
    /// #value: 100
    function test_registered_producer_purchases_complete_batch() public payable {
        (CertificateRegistry registry, CertificateMarket market, TestActor producer, TestActor buyer) = fixture();
        producer.list(market, 1, 100);
        buyer.buy{value: 100}(market, 1, 100);
        CertificateRegistry.Certificate memory certificate = registry.getCertificate(1);
        require(certificate.owner == address(buyer), "Ownership not transferred");
        require(certificate.quantity == 25, "Quantity changed");
        Assert.ok(market.credits(address(producer)) == 100, "Seller credit missing");
    }

    /// #value: 100
    function test_unregistered_purchase_reverts() public payable {
        (CertificateRegistry registry, CertificateMarket market, TestActor producer, ) = fixture();
        producer.list(market, 1, 100);
        TestActor stranger = new TestActor();
        bool rejected;
        try stranger.buy{value: 100}(market, 1, 100) {} catch { rejected = true; }
        require(market.getListing(1).active && market.totalCredits() == 0, "Sale state changed");
        Assert.ok(rejected && registry.getCertificate(1).owner == address(producer), "Unregistered purchase accepted");
    }

    // Pay the seller after a completed sale.
    /// #value: 100
    function test_seller_withdraws_sale_proceeds() public payable {
        (, CertificateMarket market, TestActor producer, TestActor buyer) = fixture();
        producer.list(market, 1, 100);
        buyer.buy{value: 100}(market, 1, 100);
        producer.withdrawProceeds(market);
        require(address(producer).balance == 100, "Proceeds not paid");
        Assert.ok(market.credits(address(producer)) == 0, "Credit not cleared");
    }

    // Retire the purchased batch while keeping its quantity.
    /// #value: 100
    function test_owner_retires_owned_batch() public payable {
        (CertificateRegistry registry, CertificateMarket market, TestActor producer, TestActor buyer) = fixture();
        producer.list(market, 1, 100);
        buyer.buy{value: 100}(market, 1, 100);
        buyer.retire(registry, 1);
        CertificateRegistry.Certificate memory certificate = registry.getCertificate(1);
        require(certificate.status == CertificateRegistry.CertificateStatus.Retired, "Not retired");
        Assert.ok(certificate.quantity == 25, "Quantity changed");
    }
}
