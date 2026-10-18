// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./TestActors.sol";
import "remix_tests.sol";

contract CertificateRegistryTest {
    // Reject a wallet address in place of the role contract.
    function test_rejects_wallet_as_role_registry() public {
        bool rejected;
        try new CertificateRegistry(address(0x1234)) {} catch {
            rejected = true;
        }
        Assert.ok(rejected, "Wallet address was accepted as role registry");
    }

    // Create a registry and a registered application wallet.
    function fixture() private returns (CertificateRegistry registry, TestActor producer) {
        RoleRegistry roles = new RoleRegistry(address(this));
        producer = new TestActor();
        producer.register(roles, 2);
        registry = new CertificateRegistry(address(roles));
    }

    // Store the quantity and Pending status of a submitted batch.
    function test_registered_buyer_submits_batch_application() public {
        (CertificateRegistry registry, TestActor producer) = fixture();
        producer.submit(registry, 1, 25);
        CertificateRegistry.Application memory application = registry.getApplication(1);
        require(application.quantity == 25, "Wrong quantity");
        Assert.ok(application.status == CertificateRegistry.ApplicationStatus.Pending, "Not pending");
    }

    function test_unregistered_wallet_cannot_submit() public {
        RoleRegistry roles = new RoleRegistry(address(this));
        CertificateRegistry registry = new CertificateRegistry(address(roles));
        TestActor stranger = new TestActor();
        bool rejected;
        try stranger.submit(registry, 1, 5) {} catch { rejected = true; }
        Assert.ok(rejected && registry.applicationCount() == 0, "Unregistered submission accepted");
    }

    // Preserve separate Withdrawn and Rejected decisions.
    function test_application_can_be_withdrawn_or_rejected() public {
        (CertificateRegistry registry, TestActor producer) = fixture();
        producer.submit(registry, 1, 5);
        producer.withdrawApplication(registry, 1);
        producer.submit(registry, 2, 10);
        registry.rejectApplication(2, bytes32(uint256(4)));
        require(registry.getApplication(1).status == CertificateRegistry.ApplicationStatus.Withdrawn, "Not withdrawn");
        Assert.ok(registry.getApplication(2).status == CertificateRegistry.ApplicationStatus.Rejected, "Not rejected");
    }

    // Issue one certificate with the approved application's quantity.
    function test_admin_approval_issues_certificate_batch() public {
        (CertificateRegistry registry, TestActor producer) = fixture();
        producer.submit(registry, 1, 40);
        registry.approveApplication(1);
        CertificateRegistry.Certificate memory certificate = registry.getCertificate(1);
        require(certificate.quantity == 40, "Quantity changed");
        require(certificate.owner == address(producer), "Wrong owner");
        Assert.ok(certificate.status == CertificateRegistry.CertificateStatus.Active, "Not active");
    }

    // Reject a repeat review after the certificate has been issued.
    function test_approval_cannot_repeat() public {
        (CertificateRegistry registry, TestActor producer) = fixture();
        producer.submit(registry, 1, 8);
        registry.approveApplication(1);
        bool rejected;
        try registry.approveApplication(1) {} catch {
            rejected = true;
        }
        Assert.ok(rejected && registry.certificateCount() == 1, "Repeat approval was accepted");
    }
}
