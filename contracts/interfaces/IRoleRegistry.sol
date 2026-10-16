// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IRoleRegistry {
    enum Role {
        None,
        Producer,
        Buyer,
        Admin
    }

    // Return the role assigned to an account.
    function roleOf(address account) external view returns (Role);
    // Return the original administrator.
    function admin() external view returns (address);
}
