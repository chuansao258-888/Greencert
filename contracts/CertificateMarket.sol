// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./interfaces/IRoleRegistry.sol";
import "./interfaces/ICertificateRegistry.sol";

contract CertificateMarket {
    struct Listing {
        uint256 certificateId;
        address seller;
        uint256 totalPriceWei;
        bool active;
    }

    IRoleRegistry public immutable roleRegistry;
    ICertificateRegistry public immutable certificateRegistry;
    mapping(uint256 => Listing) private listings;
    mapping(address => uint256) public credits;
    uint256 public totalCredits;
    uint256 public totalSalesWei;
    uint256 public soldCount;
    bool private withdrawing;

    event CertificateListed(uint256 indexed certificateId, address indexed seller, uint256 totalPriceWei);
    event ListingPriceUpdated(uint256 indexed certificateId, address indexed seller, uint256 oldTotalPriceWei, uint256 newTotalPriceWei);
    event ListingCancelled(uint256 indexed certificateId, address indexed seller);
    event CertificatePurchased(uint256 indexed certificateId, address indexed seller, address indexed buyer, uint32 quantity, uint256 totalPriceWei);
    event Withdrawal(address indexed seller, uint256 amountWei);

    // Bind the role and certificate registries.
    constructor(address roleRegistryAddress, address certificateRegistryAddress) {
        require(roleRegistryAddress != address(0) && certificateRegistryAddress != address(0), "Registry is required");
        roleRegistry = IRoleRegistry(roleRegistryAddress);
        certificateRegistry = ICertificateRegistry(certificateRegistryAddress);
    }

    // List an owned batch at one total price.
    function listCertificate(uint256 certificateId, uint256 totalPriceWei) external {
        require(roleRegistry.roleOf(msg.sender) == IRoleRegistry.Role.Producer, "Producer only");
        require(totalPriceWei > 0, "Price is required");
        require(!listings[certificateId].active, "Certificate already listed");

        certificateRegistry.setListed(certificateId, msg.sender, true);
        listings[certificateId] = Listing(certificateId, msg.sender, totalPriceWei, true);
        emit CertificateListed(certificateId, msg.sender, totalPriceWei);
    }

    // Change the total price of an active listing.
    function updatePrice(uint256 certificateId, uint256 newTotalPriceWei) external {
        Listing storage listing = activeListing(certificateId);
        require(listing.seller == msg.sender, "Seller only");
        require(newTotalPriceWei > 0, "Price is required");
        uint256 oldPrice = listing.totalPriceWei;
        listing.totalPriceWei = newTotalPriceWei;
        emit ListingPriceUpdated(certificateId, msg.sender, oldPrice, newTotalPriceWei);
    }

    // Remove a listing without changing ownership.
    function cancelListing(uint256 certificateId) external {
        Listing storage listing = activeListing(certificateId);
        require(listing.seller == msg.sender, "Seller only");
        listing.active = false;
        certificateRegistry.setListed(certificateId, msg.sender, false);
        emit ListingCancelled(certificateId, msg.sender);
    }

    // Exchange exact payment for the whole listed batch.
    function buyCertificate(uint256 certificateId, uint256 expectedPriceWei) external payable {
        Listing storage listing = activeListing(certificateId);
        require(roleRegistry.roleOf(msg.sender) == IRoleRegistry.Role.Buyer, "Buyer only");
        require(listing.seller != msg.sender, "Seller cannot buy");
        require(listing.totalPriceWei == expectedPriceWei && msg.value == expectedPriceWei, "Exact current price required");

        listing.active = false;
        certificateRegistry.transferOnSale(certificateId, listing.seller, msg.sender);
        credits[listing.seller] += msg.value;
        totalCredits += msg.value;
        totalSalesWei += msg.value;
        soldCount += 1;
        emit CertificatePurchased(
            certificateId,
            listing.seller,
            msg.sender,
            certificateRegistry.certificateQuantity(certificateId),
            msg.value
        );
    }

    // Withdraw proceeds accumulated from certificate sales.
    function withdraw() external {
        require(!withdrawing, "Withdrawal in progress");
        uint256 amount = credits[msg.sender];
        require(amount > 0, "No proceeds available");

        withdrawing = true;
        credits[msg.sender] = 0;
        totalCredits -= amount;
        (bool sent, ) = payable(msg.sender).call{value: amount}("");
        require(sent, "Transfer failed");
        withdrawing = false;
        emit Withdrawal(msg.sender, amount);
    }

    // Read a certificate's current or last listing.
    function getListing(uint256 certificateId) external view returns (Listing memory) {
        return listings[certificateId];
    }

    // Resolve an active listing or reject the request.
    function activeListing(uint256 certificateId) private view returns (Listing storage) {
        Listing storage listing = listings[certificateId];
        require(listing.active, "Certificate is not listed");
        return listing;
    }
}
