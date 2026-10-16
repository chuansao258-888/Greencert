// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./interfaces/IRoleRegistry.sol";

contract RoleRegistry is IRoleRegistry {
    address public immutable override admin;
    mapping(address => Role) private roles;

    event RoleRegistered(address indexed account, Role role);

    error AlreadyRegistered();
    error InvalidRegistrationRole();

    // Assign the initial administrator.
    constructor(address adminAddress) {
        require(adminAddress != address(0), "Admin is required");
        admin = adminAddress;
        roles[adminAddress] = Role.Admin;
    }

    // Register a wallet as a Producer or Buyer once.
    function register(uint8 requestedRole) external {
        if (roles[msg.sender] != Role.None) revert AlreadyRegistered();
        if (requestedRole != uint8(Role.Producer) && requestedRole != uint8(Role.Buyer)) {
            revert InvalidRegistrationRole();
        }

        Role selectedRole = Role(requestedRole);
        roles[msg.sender] = selectedRole;
        emit RoleRegistered(msg.sender, selectedRole);
    }

    // Return the role assigned to a wallet.
    function roleOf(address account) external view override returns (Role) {
        return roles[account];
    }
}
