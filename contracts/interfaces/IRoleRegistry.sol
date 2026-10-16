// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IRoleRegistry {
    enum Role {
        None,
        Producer,
        Buyer,
        Admin
    }

    function roleOf(address account) external view returns (Role);
    function admin() external view returns (address);
}
