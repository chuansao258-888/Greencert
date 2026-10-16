// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./interfaces/IRoleRegistry.sol";
import "./interfaces/ICertificateRegistry.sol";

interface IMarketBinding {
    // Return the role registry bound to the market.
    function roleRegistry() external view returns (address);
    // Return the certificate registry bound to the market.
    function certificateRegistry() external view returns (address);
}

contract CertificateRegistry is ICertificateRegistry {
    enum ApplicationStatus { None, Pending, Approved, Rejected, Withdrawn }
    enum CertificateStatus { None, Active, Retired }

    struct Application {
        uint256 id;
        address producer;
        bytes32 batchKey;
        bytes32 siteHash;
        uint64 periodStart;
        uint64 periodEnd;
        uint32 batchIndex;
        uint32 quantity;
        bytes32 metadataHash;
        ApplicationStatus status;
        uint256 certificateId;
        bytes32 rejectionHash;
    }

    struct Certificate {
        uint256 id;
        uint256 applicationId;
        address producer;
        address owner;
        uint32 quantity;
        bytes32 metadataHash;
        CertificateStatus status;
        bool listed;
        uint64 issuedAt;
        uint64 retiredAt;
        bytes32 retirementHash;
    }

    IRoleRegistry public immutable roleRegistry;
    address public market;
    uint256 public applicationCount;
    uint256 public certificateCount;

    mapping(uint256 => Application) private applications;
    mapping(uint256 => Certificate) private certificates;
    mapping(bytes32 => bool) public batchKeyUsed;

    event ApplicationSubmitted(uint256 indexed applicationId, address indexed producer, bytes32 indexed batchKey, uint32 quantity, bytes32 metadataHash);
    event ApplicationWithdrawn(uint256 indexed applicationId, address indexed producer);
    event ApplicationRejected(uint256 indexed applicationId, address indexed admin, bytes32 reasonHash);
    event CertificateIssued(uint256 indexed certificateId, uint256 indexed applicationId, address indexed producer, uint32 quantity, bytes32 metadataHash);
    event CertificateRetired(uint256 indexed certificateId, address indexed owner, bytes32 retirementHash, uint64 retiredAt);

    // Restrict a call to the original administrator.
    modifier onlyAdmin() {
        require(msg.sender == roleRegistry.admin(), "Admin only");
        _;
    }

    // Restrict ownership changes to the bound market.
    modifier onlyMarket() {
        require(msg.sender == market, "Market only");
        _;
    }

    // Bind the role registry used by all certificate operations.
    constructor(address roleRegistryAddress) {
        require(roleRegistryAddress.code.length > 0, "Role registry contract required");
        IRoleRegistry roles = IRoleRegistry(roleRegistryAddress);
        address adminAddress = roles.admin();
        require(adminAddress != address(0) && roles.roleOf(adminAddress) == IRoleRegistry.Role.Admin, "Invalid role registry");
        roleRegistry = roles;
    }

    // Bind the market once after all contracts are deployed.
    function setMarket(address marketAddress) external onlyAdmin {
        require(market == address(0), "Market already set");
        require(marketAddress != address(0) && marketAddress.code.length > 0, "Invalid market");
        require(IMarketBinding(marketAddress).roleRegistry() == address(roleRegistry), "Wrong role registry");
        require(IMarketBinding(marketAddress).certificateRegistry() == address(this), "Wrong certificate registry");
        market = marketAddress;
    }

    // Submit a unique generation batch for review.
    function submitApplication(
        bytes32 siteHash,
        uint64 periodStart,
        uint64 periodEnd,
        uint32 batchIndex,
        uint32 quantity,
        bytes32 metadataHash
    ) external returns (uint256 applicationId) {
        require(roleRegistry.roleOf(msg.sender) == IRoleRegistry.Role.Producer, "Producer only");
        require(siteHash != bytes32(0) && metadataHash != bytes32(0), "Hashes are required");
        require(periodStart < periodEnd && periodEnd <= block.timestamp, "Invalid period");
        require(batchIndex > 0 && quantity > 0 && quantity <= 100, "Invalid batch");

        bytes32 batchKey = keccak256(abi.encode(block.chainid, msg.sender, siteHash, periodStart, periodEnd, batchIndex));
        require(!batchKeyUsed[batchKey], "Batch already submitted");
        batchKeyUsed[batchKey] = true;

        applicationId = ++applicationCount;
        applications[applicationId] = Application({
            id: applicationId,
            producer: msg.sender,
            batchKey: batchKey,
            siteHash: siteHash,
            periodStart: periodStart,
            periodEnd: periodEnd,
            batchIndex: batchIndex,
            quantity: quantity,
            metadataHash: metadataHash,
            status: ApplicationStatus.Pending,
            certificateId: 0,
            rejectionHash: bytes32(0)
        });
        emit ApplicationSubmitted(applicationId, msg.sender, batchKey, quantity, metadataHash);
    }

    // Withdraw a pending application owned by the caller.
    function withdrawApplication(uint256 applicationId) external {
        Application storage application = applicationFor(applicationId);
        require(application.producer == msg.sender, "Application owner only");
        require(application.status == ApplicationStatus.Pending, "Application is not pending");
        application.status = ApplicationStatus.Withdrawn;
        emit ApplicationWithdrawn(applicationId, msg.sender);
    }

    // Issue one certificate containing the approved batch quantity.
    function approveApplication(uint256 applicationId) external onlyAdmin returns (uint256 certificateId) {
        Application storage application = applicationFor(applicationId);
        require(application.status == ApplicationStatus.Pending, "Application is not pending");

        application.status = ApplicationStatus.Approved;
        certificateId = ++certificateCount;
        certificates[certificateId] = Certificate({
            id: certificateId,
            applicationId: applicationId,
            producer: application.producer,
            owner: application.producer,
            quantity: application.quantity,
            metadataHash: application.metadataHash,
            status: CertificateStatus.Active,
            listed: false,
            issuedAt: uint64(block.timestamp),
            retiredAt: 0,
            retirementHash: bytes32(0)
        });
        application.certificateId = certificateId;
        emit CertificateIssued(certificateId, applicationId, application.producer, application.quantity, application.metadataHash);
    }

    // Reject a pending application with a stored reason hash.
    function rejectApplication(uint256 applicationId, bytes32 reasonHash) external onlyAdmin {
        Application storage application = applicationFor(applicationId);
        require(application.status == ApplicationStatus.Pending, "Application is not pending");
        require(reasonHash != bytes32(0), "Reason is required");
        application.status = ApplicationStatus.Rejected;
        application.rejectionHash = reasonHash;
        emit ApplicationRejected(applicationId, msg.sender, reasonHash);
    }

    // Retire the complete batch held by its Buyer owner.
    function retireCertificate(uint256 certificateId, bytes32 retirementHash) external {
        Certificate storage certificate = certificateFor(certificateId);
        require(roleRegistry.roleOf(msg.sender) == IRoleRegistry.Role.Buyer, "Buyer only");
        require(certificate.owner == msg.sender, "Certificate owner only");
        require(certificate.status == CertificateStatus.Active && !certificate.listed, "Certificate is unavailable");
        require(retirementHash != bytes32(0), "Retirement hash is required");
        certificate.status = CertificateStatus.Retired;
        certificate.retiredAt = uint64(block.timestamp);
        certificate.retirementHash = retirementHash;
        emit CertificateRetired(certificateId, msg.sender, retirementHash, certificate.retiredAt);
    }

    // Update listing state when called by the bound market.
    function setListed(uint256 certificateId, address seller, bool listed) external onlyMarket {
        Certificate storage certificate = certificateFor(certificateId);
        require(certificate.owner == seller, "Seller is not owner");
        require(certificate.status == CertificateStatus.Active, "Certificate is unavailable");
        require(certificate.listed != listed, "Listing unchanged");
        if (listed) require(roleRegistry.roleOf(seller) == IRoleRegistry.Role.Producer, "Producer only");
        certificate.listed = listed;
    }

    // Transfer an entire listed batch to the Buyer.
    function transferOnSale(uint256 certificateId, address seller, address buyer) external onlyMarket {
        Certificate storage certificate = certificateFor(certificateId);
        require(certificate.owner == seller && certificate.listed, "Certificate is not listed");
        require(certificate.status == CertificateStatus.Active, "Certificate is unavailable");
        require(roleRegistry.roleOf(buyer) == IRoleRegistry.Role.Buyer, "Buyer only");
        certificate.owner = buyer;
        certificate.listed = false;
    }

    // Read one stored application.
    function getApplication(uint256 applicationId) external view returns (Application memory) {
        return applicationFor(applicationId);
    }

    // Read one issued certificate.
    function getCertificate(uint256 certificateId) external view returns (Certificate memory) {
        return certificateFor(certificateId);
    }

    // Return the immutable quantity of an issued batch.
    function certificateQuantity(uint256 certificateId) external view returns (uint32) {
        return certificateFor(certificateId).quantity;
    }

    // Resolve a valid application index.
    function applicationFor(uint256 applicationId) private view returns (Application storage) {
        require(applicationId > 0 && applicationId <= applicationCount, "Unknown application");
        return applications[applicationId];
    }

    // Resolve a valid certificate index.
    function certificateFor(uint256 certificateId) private view returns (Certificate storage) {
        require(certificateId > 0 && certificateId <= certificateCount, "Unknown certificate");
        return certificates[certificateId];
    }
}
