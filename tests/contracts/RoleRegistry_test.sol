// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./TestActors.sol";
import "remix_tests.sol";

contract RoleRegistryTest {
    // Register separate Producer and Buyer wallets.
    function test_registers_producer_and_buyer() public {
        RoleRegistry roles = new RoleRegistry(address(this));
        TestActor producer = new TestActor();
        TestActor buyer = new TestActor();
        producer.register(roles, 1);
        buyer.register(roles, 2);
        require(roles.roleOf(address(producer)) == IRoleRegistry.Role.Producer, "Producer role missing");
        Assert.ok(roles.roleOf(address(buyer)) == IRoleRegistry.Role.Buyer, "Buyer role missing");
    }

    // Refuse a second registration from the same wallet.
    function test_rejects_role_change() public {
        RoleRegistry roles = new RoleRegistry(address(this));
        TestActor producer = new TestActor();
        producer.register(roles, 1);
        bool rejected;
        try producer.register(roles, 2) {} catch {
            rejected = true;
        }
        Assert.ok(rejected && roles.roleOf(address(producer)) == IRoleRegistry.Role.Producer, "Role change was accepted");
    }
}
