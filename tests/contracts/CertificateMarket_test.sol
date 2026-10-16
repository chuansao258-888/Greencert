// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./TestActors.sol";

contract CertificateMarketTest {
    // Deploy a listed batch and separate Producer and Buyer actors.
    function fixture() private returns (CertificateRegistry registry, CertificateMarket market, TestActor producer, TestActor buyer) {
        RoleRegistry roles = new RoleRegistry(address(this));
        producer = new TestActor();
        buyer = new TestActor();
        producer.register(roles, 1);
        buyer.register(roles, 2);
        registry = new CertificateRegistry(address(roles));
        market = new CertificateMarket(address(roles), address(registry));
        registry.setMarket(address(market));
        producer.submit(registry, 1, 25);
        registry.approveApplication(1);
    }

    // List, reprice and cancel the complete certificate batch.
    function test_producer_lists_updates_and_cancels() public {
        (CertificateRegistry registry, CertificateMarket market, TestActor producer, ) = fixture();
        producer.list(market, 1, 100);
        producer.updatePrice(market, 1, 120);
        require(market.getListing(1).totalPriceWei == 120, "Price not updated");
        producer.cancel(market, 1);
        require(!registry.getCertificate(1).listed, "Listing not cancelled");
    }

    // Purchase the complete batch for its exact total price.
    /// #value: 100
    function test_buyer_purchases_complete_batch() public payable {
        (CertificateRegistry registry, CertificateMarket market, TestActor producer, TestActor buyer) = fixture();
        producer.list(market, 1, 100);
        buyer.buy{value: 100}(market, 1, 100);
        CertificateRegistry.Certificate memory certificate = registry.getCertificate(1);
        require(certificate.owner == address(buyer), "Ownership not transferred");
        require(certificate.quantity == 25, "Quantity changed");
        require(market.credits(address(producer)) == 100, "Seller credit missing");
    }

    // Pay the seller after a completed sale.
    /// #value: 100
    function test_seller_withdraws_sale_proceeds() public payable {
        (, CertificateMarket market, TestActor producer, TestActor buyer) = fixture();
        producer.list(market, 1, 100);
        buyer.buy{value: 100}(market, 1, 100);
        producer.withdrawProceeds(market);
        require(address(producer).balance == 100, "Proceeds not paid");
        require(market.credits(address(producer)) == 0, "Credit not cleared");
    }

    // Retire the purchased batch while keeping its quantity.
    /// #value: 100
    function test_buyer_retires_owned_batch() public payable {
        (CertificateRegistry registry, CertificateMarket market, TestActor producer, TestActor buyer) = fixture();
        producer.list(market, 1, 100);
        buyer.buy{value: 100}(market, 1, 100);
        buyer.retire(registry, 1);
        CertificateRegistry.Certificate memory certificate = registry.getCertificate(1);
        require(certificate.status == CertificateRegistry.CertificateStatus.Retired, "Not retired");
        require(certificate.quantity == 25, "Quantity changed");
    }
}
